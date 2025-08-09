Here’s a more detailed analysis with proof:

**Bytecode in benchmarks.**
I analyzed the bytecode for Scala 2 and Scala 3 and found no significant differences at the call site of `map`.
When passing a method to `map`, the compiler generates a specialized lambda `apply$mcII$sp (int -> int)`, which avoids boxing at the call site.
When passing a regular lambda, it compiles to `Function1<Object, Object>`, and boxing occurs during the invocation.

```java
// method -> specialized lambda (identical for oldMap/newMap)
bh.consume(ArrayOpsCompat.ArrayOpsExt$.MODULE$.newMap$extension(
  ArrayOpsCompat$.MODULE$.ArrayOpsExt(this.array()),
  (JFunction1.mcII.sp)(x) -> this.heavy(x),
  scala.reflect.ClassTag$.MODULE$.Int()
));

// regular lambda -> (Object-> Object)
bh.consume(ArrayOpsCompat.ArrayOpsExt$.MODULE$.newMap$extension(
  ArrayOpsCompat$.MODULE$.ArrayOpsExt(this.array()),
  (Object x) -> this.genericHeavy(x),
  scala.reflect.ClassTag$.MODULE$.Object()
));
```

**Bytecode inside method implementations.**
The differences appear inside the implementations of `oldMap$extension` and `newMap$extension`.
The old version `oldMap` contains a type switch for all primitive and reference array types.
In the `int[]` branch, primitives are explicitly boxed via `BoxesRunTime.boxToInteger` before calling `f.apply(...)`. This large branching structure makes the method big and harder for the JIT to optimize.
The new version `newMap` is linear: a single loop without type matching, minimal extra code.

```java
// oldMap
if ($this instanceof int[]) {
    for (int[] arr = (int[]) $this; i < len; ++i) {
        ys[i] = f.apply(BoxesRunTime.boxToInteger(arr[i]));
    }
} else if ($this instanceof double[]) {
    // branch for double[]
}
// ... other primitive array branches ...
```

```java
// newMap
for (int i = 0; i < len; i++) {
    ys[i] = f.apply(xs[i]);
}
```

**JIT log summary.**
DISCLAIMER: I'm inspecting the log manually, so it is possible that can miss something.

Analysis of the JIT logs shows that specialized lambda calls (`apply$mcII$sp`) **were inlined in all cases**.
The key difference is that `oldMap` sometimes **fails to be fully inlined** because the method is too large. This likely prevents the JIT from performing further optimizations, such as eliminating boxing inside the loop.
In contrast, `newMap` is smaller, allowing the JIT to inline it completely and apply all possible optimizations.

```xml
<!-- context: call to benchmarks.ArrayOpsCompat$ArrayOpsExt$.oldMap$extension -->
<method id='1421' holder='benchmarks.ArrayOpsCompat$ArrayOpsExt$' name='oldMap$extension' bytes='599' compiler='c2' level='4'/>
<call method='1421' inline='1'/>
<inline_fail reason='hot method too big'/>

<!-- context: call to benchmarks.ArrayOpsCompat$ArrayOpsExt$.newMap$extension -->
<method id='1444' holder='benchmarks.ArrayOpsCompat$ArrayOpsExt$' name='newMap$extension' bytes='63' compiler='c1' level='3'/>
<call method='1444' inline='1'/>
<inline_success reason='inline (hot)'/>

<method id='1507' holder='scala/runtime/java8/JFunction1$mcII$sp' name='apply$mcII$sp' return='int' arguments='int' compiler='c1' level='3'/>
<call method='1507' inline='1'/>
<inline_success reason='inline (hot)'/>
```

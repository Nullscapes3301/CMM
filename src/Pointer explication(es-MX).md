# Punteros en CMM

## Definicion

En CMM los punteros no son como en C++. En C++ los punteros apuntan a **una direccion en memoria**, pero en CMM los punteros apuntan directamente a la variable, es decir, guarda **el nombre de la variable en texto plano**, por ejemplo:

```CMM
cmm-dvar((x)ac(txt(Hola mundo!))),dvar((&y)ac(txt(x))).
```

En ese codigo ejemplo es algo asi

```Pseudo
x = "Hola mundo!"
&y = "x"
```

La variable &y si se llama &y , el & al inicio indica que **es un puntero**
Al hacer

```CMM
cmm-dvar((x)ac(txt(Hola mundo!))),dvar((&y)ac(txt(x))),nvar((&y)ac(txt(Adios mundo!))).
```

El nvar no modificaria la variable &y a "Adios mundo!", modificaria la variable con el nombre que tiene el contenido en el &y, este caso "x" osea: la variable x entonces

```CMM
cmm-dvar((x)ac(num(0))),dvar((&y)ac(txt(x))),pr(var(x)),nvar((&y)ac(num(1))),pr(var(x)).
```

Va a mostrar

```output
0
1
```

Aparte si muestras el puntero directamente mostara **la variable** a la que apunta por ejemplo

```CMM
cmm-dvar((x)ac(txt(Hola mundo!))),dvar((&y)ac(txt(x))),pr(var(&y)).
```

```output
Hola mundo!
```

## Entonces como se modifica el contenido de una variable puntero? (Cambiar a que variable apunta)

Con otro puntero xd (nvar no modificaria el puntero, modificara al que apunta)

```CMM
cmm-dvar((msg1)ac(txt(Hola mundo!))),dvar((msg2)ac(txt(Adios mundo!))),dvar((&p1)ac(txt(msg1))),dvar((&p2)ac(txt(&p1))),pr(var(&p1)),nvar((&p2)ac(txt(msg2))),pr(var(&p1)).
```

```output
Hola mundo!
Adios mundo!
```

## Y como se ve a que apunta?

Con otro puntero xd (var no mostraria el puntero, mostraria el valor del que apunta)

```CMM
cmm-dvar((msg)ac(txt(Hola mundo!))),dvar((&ptr)ac(txt(msg))),dvar((&ktr)ac(txt(&ptr))),pr(txt(Esto no muestra a que apunta -> ),var(msg)),pr(txt(Esto si -> ),var(&ktr)).
```

```output
Esto no muestra a que apunta -> Hola mundo!
Esto si -> msg
```

## Algo mas?

Sí.
Un puntero no puede apuntar a una *constante*, *builtin*, o a una variable que no existe; solo a una *variable* o a otro *puntero*.

```CMM
cmm-dvar((&p)ac(txt(x))).
```

```output
VarNotExistError: Variable 'x' doesn't exists
In block 1
dvar((&p)ac(txt(x)))
^~~~~~~~~~~~~~~~~~~~
```

```CMM
cmm-dvar((&x)ac(txt(__name__))).
```

```output
<------------------- CMM error
PointerError: Cannot point to a builtin variable
In block 1
dvar((&x)ac(txt(__name__)))
^~~~~~~~~~~~~~~~~~~~~~~~~~~
```

```CMM
cmm-dvar((*const)ac(txt(Hola mundo!))),dvar((&p)ac(txt(*const))).
```

```output
<------------------- CMM error
PointerError: Cannot point to a constant
In block 2
dvar((&p)ac(txt(*const)))
^~~~~~~~~~~~~~~~~~~~~~~~~
```

Para no confundir con las variables tenemos este grafico

|Modelo   | Tipo        | Creable | Modificable |
|-----------------------------------------------|
| var     | Variable    | Sí      | Sí          |
| *var    | Constante   | Sí      | No          |
| &var    | Puntero     | Sí      | Sí          |
| \_\_var__ | Builtin     | No      | No          |

## Y la recursion infinita con un puntero que apunta a otro y este otro apunta al original?

No existe. Y si te preguntas porque vuelve a leer el manual.

### Ciclo directo

```CMM
cmm-dvar((&a)ac(txt(&b))),dvar((&b)ac(txt(&a))).
```

```output
<------------------- CMM error
VarNotExistError: Variable '&b' doesn't exists
In block 1
dvar((&a)ac(txt(&b)))
^~~~~~~~~~~~~~~~~~~~~
```

### Ciclo indirecto

```CMM
cmm-dvar((temp)ac(None)),dvar((&a)ac(txt(temp))),dvar((&b)ac(txt(&a))),dvar((&t)ac(txt(&a))),nvar((&t)ac(txt(&b))),pr(var(&a))
```

```output
&a
```

Y se preguntan, **Porque?**

Porque a dvar o a nvar o a var les vale tres toneladas de verga que apuntes a un puntero,  nvar modificara al apuntado y  var mostrara el valor del apuntado, no hacen una recursion para obterner el primer valor qu eno sea puntero

## Los comandos de las variables con punteros

Antes de empezar esta seccion veamos sus definiciones

`dvar((var_name)ac(Content))` -> Declarar variable, constante o puntero
`nvar((var_name)ac(Content))` -> Modificar variable o puntero(con otro puntero)
`var(var_name)` -> obtener el contenido de una variable

Entonces

`dvar((var)ac(txt(Hola mundo!)))` -> crea variable *var*
`dvar((*const)ac(txt(Hola mundo!)))` -> crea constante *\*const*
`dvar((&ptr)ac(txt(var1)))` -> crea puntero *&ptr* apuntando a *var1*
`dvar((__var__)ac(txt(Hola mundo!)))` -> error

Al crear un puntero con dvar, dvar verificar si la variable a la que apunta existe. Y le asigna algo asi

```JSON
{"&ptr": "x"}
```

`nvar((var)ac(txt(Hola mundo!)))` -> modificar la variable *var*
`nvar((*const)ac(txt(Hola mundo!)))` -> error
`nvar((&ptr)ac(txt(Hola mundo)))` -> Modifica a la variable que tiene el nombre que almacena *&ptr*
`nvar((__var__)ac(txt(Hola mundo!)))` -> error

Y con var

`var(var)` -> Muestra el valor almacenado dentro de la variable *var*
`var(*var)` -> Muestra el valor almacenado dentro de la constante *\*var*
`var(&var)` -> Muestra el valor almacenado dentro de la que tiene el nombre almacenado dentro del puntero
`var(__var__)` -> Muestra el valor almacenado dentro de la builtin *\_\_var__*

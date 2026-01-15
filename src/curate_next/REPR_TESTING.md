karlal_bin@karlal
~/dev/project/packages/curate
$ python
Python 3.10.12 (main, Jan  8 2026, 06:52:19) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from curate_next import compile_scope_set
>>> from curate_next.facts import Scope, ScopeSet
>>>
>>> src = ""
>>> scopes = compile_scope_set(source=src)
>>> scopes
ScopeSet(scopes=(Scope(id=0, parent_id=None, kind='module', start=1, end=1),))
>>>
>>> for s in scopes:
...     print(s)
...
Scope(id=0, parent_id=None, kind='module', start=1, end=1)
>>> len(scopes)
1
>>> scopes[0]
Scope(id=0, parent_id=None, kind='module', start=1, end=1)
>>> scopes[:]
ScopeSet(scopes=(Scope(id=0, parent_id=None, kind='module', start=1, end=1),))
>>>
>>> src = '''
... def foo(x):
...     if x > 0:
...         return x
...
... def bar():
...     pass
... '''
>>> scopes = compile_scope_set(source=src, language="python")
>>> scopes
ScopeSet(scopes=(Scope(id=0, parent_id=None, kind='module', start=1, end=8), Scope(id=1, parent_id=0, kind='function_definition', start=2, end=4), Scope(id=2, parent_id=1, kind='if_statement', start=3, end=4), Scope(id=3, parent_id=0, kind='function_definition', start=6, end=7)))
>>> scopes2 = compile_scope_set(source=src, language="python")
>>> scopes == scopes2
True
>>> from curate_next import build_index, scope_at_line>>>
>>> idx = build_index(scopes)
>>> idx
Index(scopes=(Scope(id=0, parent_id=None, kind='module', start=1, end=8), Scope(id=1, parent_id=0, kind='function_definition', start=2, end=4), Scope(id=2, parent_id=1, kind='if_statement', start=3, end=4), Scope(id=3, parent_id=0, kind='function_definition', start=6, end=7)), by_id={0: Scope(id=0, parent_id=None, kind='module', start=1, end=8), 1: Scope(id=1, parent_id=0, kind='function_definition', start=2, end=4), 2: Scope(id=2, parent_id=1, kind='if_statement', start=3, end=4), 3: Scope(id=3, parent_id=0, kind='function_definition', start=6, end=7)}, parent={0: None, 1: 0, 2: 1, 3: 0}, children={0: (1, 3), 1: (2,)}, starts=(1, 2, 3, 6), ends=(8, 4, 4, 7))
>>> scope_at_line(idx, 3)
Scope(id=2, parent_id=1, kind='if_statement', start=3, end=4)
>>>
>>> from curate_next import relations
>>>
>>> s = scope_at_line(idx, 3)
>>> relations.parent(idx, s)
Scope(id=1, parent_id=0, kind='function_definition', start=2, end=4)
>>> relations.ancestors(idx, s)
(Scope(id=1, parent_id=0, kind='function_definition', start=2, end=4), Scope(id=0, parent_id=None, kind='module', start=1, end=8))
>>> relations.children(idx, s)
()
>>> from curate_next.query import Query, query_ranges
>>>
>>> query_ranges(
... source=src,
... cursor=3,
... query=Query(axis="ancestors"),
... language="python",
... )
[(1, 8), (2, 4)]

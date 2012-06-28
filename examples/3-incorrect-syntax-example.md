# Extended markdown syntax example #3

-- row 4, 4, 4 --
This is a demonstration for incomplete grid markup processing.

-- row 2, 2 --
This row has not enough columns defined.
--
There are 4 columns but the number or row marker arguments is 2.
--
In this case the last two columns will have `default_col_class`
value for the class HTML element attribute.
--
...
-- end --

--
Row #3 starts here.

-- row 1, 2, 3, 4, 5 --
This row has more arguments than require.
--
But this is not a problem.
The unused ones will be ignored.
-- end --

Row #3 ends here but there are no terminating marker.
In this case the row will be closed in the end of the document.

-- row 4, 4, 4 --

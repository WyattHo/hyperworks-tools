# NodeCr
*createnodesbetweenpositions -40.0000007 -60.0000027 -0.5 -40.0000017 -60 0 1 0 0
*loadtype 10 1

# MPC created
*createmark nodes 2 7118 7123
*createarray 2 1 1
*createdoublearray 12 1 1 1 1 1 1 1 1 1 1 1 1
*equationcreate 2 1 2 1 12 7136 1 -1 0
*createmark equations 1 1
*findmark equations 1 0 1 equations 0 0;

# Modified Dependent dof of Equation
*setvalue equations id=1 STATUS=2 dependentdof=3

# Attached attributes to Equation
*setvalue equations id=1 STATUS=2 3263=0
*mergehistorystate "" ""

# Modified WF 3 of Equation
*setvalue equations id=1 STATUS=2 ROW=0 independentcoeffs3= {1}
*setvalue equations id=1 STATUS=2 ROW=1 independentcoeffs3= {}

# Modified WF 3 of Equation
*setvalue equations id=1 STATUS=2 ROW=0 independentcoeffs3= {1}
*setvalue equations id=1 STATUS=2 ROW=1 independentcoeffs3= {-1}

# Modified WF 1 of Equation
*setvalue equations id=1 STATUS=2 ROW=0 independentcoeffs1= {}
*setvalue equations id=1 STATUS=2 ROW=1 independentcoeffs1= {1}

# Modified WF 1 of Equation
*setvalue equations id=1 STATUS=2 ROW=0 independentcoeffs1= {}
*setvalue equations id=1 STATUS=2 ROW=1 independentcoeffs1= {}

# Modified Dependent coeff of Equation
*setvalue equations id=1 STATUS=2 dependentcoeff=1
*createentity loadcols includeid=0 name="loadcol1"
*clearmark loadcols 1

# Renamed Load Collector from "loadcol1" to "MPC"
*setvalue loadcols id=4 name=MPC

# Moved equations into component "MPC"
*createmark equations 1 1
*movemark equations 1 "MPC"

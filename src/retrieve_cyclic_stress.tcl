proc initial_csv {node_idx} {
    set filepath [model GetFileName]
    set idx_str [expr [string last "\\" $filepath] + 1]
    set idx_end [expr [string length $filepath] - 5]
    set prename [string range $filepath $idx_str $idx_end]
    set filename "$prename\_N$node_idx"
    set csv [open "$filename.csv" w+]
    puts $csv "angle,stress"
    return $csv
}


proc retrieve_node_stress {node_idx} {
    # get handle
    model GetQueryCtrlHandle query

    # selection
    set nodeset_idx [model AddSelectionSet node]
    model GetSelectionSetHandle nodeset $nodeset_idx
    nodeset Add "id $node_idx"

    # guery
    query SetSelectionSet $nodeset_idx
    query SetQuery "contour.value"
    query GetIteratorHandle iterator
    set data [iterator GetDataList]

    # release handle
    iterator ReleaseHandle
    nodeset ReleaseHandle
    query ReleaseHandle

    return $data
}


proc iterate_angle {angle_inc node_idx} {
    hwc animate mode modal
    hwc animate modal increment $angle_inc
    hwc animate frame 1
    set csv [initial_csv $node_idx]
    set angle 0
    set angle_end [expr {360 - $angle_inc}]
    while {True} {
        set data [retrieve_node_stress $node_idx]
        puts "$angle,$data"
        puts $csv "$angle,$data"
        hwc animate next
        set angle [expr {$angle + $angle_inc}]
        if {$angle >= $angle_end} {
            break
        }
    }
    close $csv
}


# configurations
set node_idx "138783"
set legend_format fixed
set legend_precision 1
set deform_scale 1.0
set angle_inc 1


# get contour-control handle
hwi GetSessionHandle session
session GetProjectHandle project
project GetPageHandle page [project GetActivePage]
page GetWindowHandle window [page GetActiveWindow]
window GetClientHandle client
client GetModelHandle model [client GetActiveModel]
model GetResultCtrlHandle result
result GetContourCtrlHandle contour
contour GetLegendHandle legend


# contour settings
contour SetDataType "Element Stresses (2D & 3D)"
contour SetDataComponent component "ZZ"
contour SetAverageMode "advanced"
contour SetEnableState "True"
contour SetShellLayer "max"
hwc scale deformed resulttype=Displacement value=$deform_scale


# legend settings
hwc show legends
legend SetType dynamic
hwc result scalar legend layout format=$legend_format
hwc result scalar legend layout precision=$legend_precision
hwc result scalar legend values maximum=false
hwc result scalar legend values minimum=false
hwc result scalar legend values localmaximum=false
hwc result scalar legend values localminimum=false


# iterate simulations
iterate_angle $angle_inc $node_idx


# cleanup handles to avoid leaks and handle name collisions
legend ReleaseHandle
contour ReleaseHandle
result ReleaseHandle
model ReleaseHandle
client ReleaseHandle
window ReleaseHandle
page ReleaseHandle
project ReleaseHandle
session ReleaseHandle

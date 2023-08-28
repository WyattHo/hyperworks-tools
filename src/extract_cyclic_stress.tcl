proc get_prename_of_csv {} {
    set filepath [model GetFileName]
    set idx_str [expr [string last "\\" $filepath] + 1]
    set idx_end [expr [string length $filepath] - 5]
    set filename_a [string range $filepath $idx_str $idx_end]
    set filename_b "cyclic_stress"
    return "$filename_a$filename_b"
}


proc initial_csv {prename subcase_idx} {
    set csv [open "$prename$subcase_idx.csv" w+]
    puts $csv "angle,stress"
    return $csv
}


proc get_maximum_stress_and_save_data {simu_label csv} {
    set max_stress [measure GetMaximum scalar]
    set idx_str [expr [string first = $simu_label] + 2]
    set frequency [string range $simu_label $idx_str end]
    puts $csv "$frequency,$max_stress"
}


proc iterate_angle {angle_inc} {
    hwc animate mode modal
    hwc animate modal increment $angle_inc
    hwc animate frame 1

    set angle 0
    set angle_end [expr {360 - $angle_inc}]
    while {True} {
        hwc animate next
        set angle [expr {$angle + $angle_inc}]
        if {$angle >= $angle_end} {
            break
        }
    }
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
# page GetAnimatorHandle animator
# client GetMeasureHandle measure 1


# contour settings
contour SetDataType "Element Stresses (2D & 3D)"
contour SetDataComponent component vonMises
contour SetAverageMode advanced
contour SetEnableState True
contour SetShellLayer max
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
iterate_angle $angle_inc


# cleanup handles to avoid leaks and handle name collisions
# animator ReleaseHandle
# measure ReleaseHandle
legend ReleaseHandle
contour ReleaseHandle
result ReleaseHandle
model ReleaseHandle
client ReleaseHandle
window ReleaseHandle
page ReleaseHandle
project ReleaseHandle
session ReleaseHandle

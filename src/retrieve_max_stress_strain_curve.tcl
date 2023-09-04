proc get_prename_of_csv {} {
    set filepath [model GetFileName]
    set idx_str [expr [string last "\\" $filepath] + 1]
    set idx_end [expr [string length $filepath] - 5]
    set filename_a [string range $filepath $idx_str $idx_end]
    set filename_b "_maximum_stress_subcase"
    return "$filename_a$filename_b"
}


proc initial_csv {prename subcase_idx} {
    set csv [open "$prename$subcase_idx.csv" w+]
    puts $csv "time,max_strain,max_stress"
    return $csv
}


proc get_maximum_stress_and_save_data {simu_label csv} {
    set max_stress [measure GetMaximum scalar]
    set idx_str [expr [string first = $simu_label] + 2]
    set time [string range $simu_label $idx_str end]
    puts $csv "$time,$max_stress"
}


proc process_subcase {subcase_idx csv} {
    set simu_num [llength [result GetSimulationList $subcase_idx]]
    for {set simu_idx 0} {$simu_idx < $simu_num} {incr simu_idx} {
        puts $simu_idx
        result SetCurrentSimulation $simu_idx
        hwc animate mode static
        set simu_label [result GetSimulationLabel $subcase_idx $simu_idx]
        get_maximum_stress_and_save_data $simu_label $csv
    }
}


# configurations
set component_indices "1"
set subcase_indices "1"
set legend_format "dynamic"
set legend_precision 1
set deform_scale 1.0

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
puts qweqwe


# specify the components in contour
set set_idx [model AddSelectionSet element]
model GetSelectionSetHandle selectionset $set_idx
foreach component_idx $component_indices {
    selectionset Add "component $component_idx"
}
contour SetSelectionSet $set_idx


# contour settings
hwc result scalar load type="Element Strains (2D & 3D)" component="ZZ" avgmode="advanced"
hwc scale deformed resulttype=Displacement value=$deform_scale


# legend settings
hwc show legends
hwc result scalar legend layout format=$legend_format
hwc result scalar legend layout precision=$legend_precision
hwc result scalar legend values maximum=false
hwc result scalar legend values minimum=false
hwc result scalar legend values localmaximum=false
hwc result scalar legend values localminimum=false


# iterate simulations
client GetMeasureHandle measure 1
page GetAnimatorHandle animator
set prename [get_prename_of_csv]
foreach subcase_idx $subcase_indices {
    puts $subcase_idx
    result SetCurrentSubcase $subcase_idx
    set csv [initial_csv $prename $subcase_idx]
    process_subcase $subcase_idx $csv
    close $csv
}


# cleanup handles to avoid leaks and handle name collisions
animator ReleaseHandle
measure ReleaseHandle
legend ReleaseHandle
contour ReleaseHandle
selectionset ReleaseHandle
result ReleaseHandle
model ReleaseHandle
client ReleaseHandle
window ReleaseHandle
page ReleaseHandle
project ReleaseHandle
session ReleaseHandle

# get contour-control handle
hwi GetSessionHandle session
session GetProjectHandle project
project GetPageHandle page [project GetActivePage]
page GetWindowHandle window [page GetActiveWindow]
window GetClientHandle client
client GetModelHandle model [client GetActiveModel]
model GetResultCtrlHandle result
result GetContourCtrlHandle contour


# contour settings
contour SetDataType "Element Stresses (2D & 3D)"
contour SetDataComponent component vonMises
contour SetAverageMode advanced
contour SetEnableState True


# specify the components in contour
set set_idx [model AddSelectionSet element]
model GetSelectionSetHandle selectionset $set_idx
selectionset Add "component 1"
selectionset Add "component 2"
selectionset Add "component 3"
contour SetSelectionSet $set_idx


# iterate simulations
set loop_inc 30
client GetMeasureHandle measure 1
set subcases [result GetSubcaseList "Base"]
foreach subcase $subcases {
    result SetCurrentSubcase $subcase
    set simu_num [llength [result GetSimulationList $subcase]]
    for {set simu_idx 0} {$simu_idx < $simu_num} {incr simu_idx} {
        result SetCurrentSimulation $simu_idx
        page GetAnimatorHandle animator
        set end_frame [animator GetEndFrame]
        hwc animate mode modal
        hwc animate modal increment $loop_inc
        for {set frame_idx 0} {$frame_idx < $end_frame} {incr frame_idx} {
            set angle [expr $frame_idx * $loop_inc]
            if {$angle > 180} {
                break
            }
            hwc animate frame [expr $frame_idx + 1]
        }
        set max_stress [measure GetMaximum scalar]
        puts "subcase: $subcase, simu_idx: $simu_idx, max_stress: $max_stress"
        animator ReleaseHandle
    }
}


# cleanup handles to avoid leaks and handle name collisions
measure ReleaseHandle
contour ReleaseHandle
selectionset ReleaseHandle
result ReleaseHandle
model ReleaseHandle
client ReleaseHandle
window ReleaseHandle
page ReleaseHandle
project ReleaseHandle
session ReleaseHandle

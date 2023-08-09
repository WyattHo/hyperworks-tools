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


# iterate simulations
client GetMeasureHandle measure 1
set subcases [result GetSubcaseList "Base"]
foreach subcase $subcases {
    result SetCurrentSubcase $subcase
    puts "subcase: $subcase"

    set simu_num [llength [result GetSimulationList $subcase]]
    for {set simu_idx 0} {$simu_idx < $simu_num} {incr simu_idx} {
        result SetCurrentSimulation $simu_idx

        client Draw
        set max_stress [measure GetMaximum scalar]
        puts $max_stress
    }
}

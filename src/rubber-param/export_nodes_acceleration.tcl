proc create_empty_curve {page_idx window_idx} {
    set range_window "p:$page_idx w:$window_idx"
    hwc xy curve create range=$range_window
}


proc assign_data_x {range_curve h3d_path subcase_name node_label} {
    hwc xy curve edit range=$range_curve xfile=$h3d_path
    hwc xy curve edit range=$range_curve xsubcase=$subcase_name
    hwc xy curve edit range=$range_curve xtype="Acceleration (Grids)"
    hwc xy curve edit range=$range_curve xrequest=$node_label
    hwc xy curve edit range=$range_curve xcomponent="Time"
}


proc assign_data_y {range_curve h3d_path subcase_name node_label} {
    hwc xy curve edit range=$range_curve yfile=$h3d_path
    hwc xy curve edit range=$range_curve ysubcase=$subcase_name
    hwc xy curve edit range=$range_curve ytype="Acceleration (Grids)"
    hwc xy curve edit range=$range_curve yrequest=$node_label
    hwc xy curve edit range=$range_curve ycomponent="MAG | X"
}


proc create_curves {page_idx window_idx h3d_path subcase_name nodes} {
    foreach node_idx $nodes {
        set node_label "N$node_idx"
        set line_idx [expr [lsearch $nodes $node_idx] + 1]
        set range_curve "p:$page_idx w:$window_idx i:$line_idx"
        create_empty_curve $page_idx $window_idx
        assign_data_x $range_curve $h3d_path $subcase_name $node_label
        assign_data_y $range_curve $h3d_path $subcase_name $node_label
    }
}


proc export_csv {h3d_path} {
    set len [string length $h3d_path]
    set model_name [string range $h3d_path 0 [expr $len - 5]]
    set suffix "subcase2"
    set csv_path "$model_name-$suffix.csv"

    hwi GetSessionHandle sess
    sess GetClientManagerHandle pm Plot
    pm GetExportCtrlHandle exp
    exp SetFormat "CSV Blocks"
    exp SetFilename $csv_path
    exp Export
}


proc get_current_file_name {} {
    # Get the current file name
    hwi GetSessionHandle session_handle
    session_handle GetProjectHandle project_handle
    project_handle GetPageHandle page_handle [project_handle GetActivePage]
    page_handle GetWindowHandle window_handle [page_handle GetActiveWindow]
    window_handle GetClientHandle client_handle
    client_handle GetModelHandle model_handle [client_handle GetActiveModel]
    set file_name [model_handle GetFileName]

    # release handles
    session_handle ReleaseHandle
    project_handle ReleaseHandle
    page_handle ReleaseHandle
    window_handle ReleaseHandle
    client_handle ReleaseHandle
    model_handle ReleaseHandle

    # return
    return $file_name
}


proc main {argv} {
    # Parse arguments
    if {[lindex $argv 1] == "-tcl"} {
        lassign [lrange $argv 3 end] h3d_path nodes
        set exit "true"
    } else {
        set h3d_path [get_current_file_name]
        set nodes "2357428,2357684,2328963,2325886"
        set exit "false"
    }
    set h3d_path [string map {\\ /} $h3d_path]
    set nodes [split $nodes ","]
    
    # Constants
    set page_idx "1"
    set window_idx "2"
    set subcase_name "Subcase 2 (FRF_X)"

    # Manipulate the page and windows
    hwc open animation modelandresult $h3d_path $h3d_path
    hwc hwd page current layout=1 activewindow=$window_idx
    hwc hwd window type="HyperGraph 2D"
    create_curves $page_idx $window_idx $h3d_path $subcase_name $nodes

    # Export and exit
    export_csv $h3d_path
    if {$exit} {
        hwc hwd exit
    }
}


main $argv

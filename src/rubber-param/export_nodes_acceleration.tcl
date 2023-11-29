proc assign_data_x {range_curve h3d_path subcase_name node_label result_type} {
    hwc xy curve edit range=$range_curve xfile=$h3d_path
    hwc xy curve edit range=$range_curve xsubcase=$subcase_name
    hwc xy curve edit range=$range_curve xtype=$result_type
    hwc xy curve edit range=$range_curve xrequest=$node_label
    hwc xy curve edit range=$range_curve xcomponent="Time"
}


proc assign_data_y {range_curve h3d_path subcase_name node_label result_type result_comp} {
    hwc xy curve edit range=$range_curve yfile=$h3d_path
    hwc xy curve edit range=$range_curve ysubcase=$subcase_name
    hwc xy curve edit range=$range_curve ytype=$result_type
    hwc xy curve edit range=$range_curve yrequest=$node_label
    hwc xy curve edit range=$range_curve ycomponent=$result_comp
}


proc get_subcase_name {subcase_idx} {
    hwi OpenStack
    hwi GetSessionHandle session_handle
    session_handle GetProjectHandle project_handle
    project_handle GetPageHandle page_handle [project_handle GetActivePage]
    page_handle GetWindowHandle window_handle "1"
    window_handle GetClientHandle client_handle
    client_handle GetModelHandle model_handle "1"
    model_handle GetResultCtrlHandle result_handle
    set subcase_name [result_handle GetSubcaseLabel $subcase_idx]
    hwi CloseStack
    return $subcase_name
}


proc create_curves {range_window h3d_path subcase_idx nodes result_type result_comp} {
    set subcase_name [get_subcase_name $subcase_idx]
    foreach node_idx $nodes {
        set node_label "N$node_idx"
        set line_idx [expr [lsearch $nodes $node_idx] + 1]
        set range_curve "$range_window i:$line_idx"
        hwc xy curve create range=$range_window
        assign_data_x $range_curve $h3d_path $subcase_name $node_label $result_type
        assign_data_y $range_curve $h3d_path $subcase_name $node_label $result_type $result_comp
    }
}


proc export_csv {h3d_path range_window subcase_idx result_name} {
    # Assign the path
    set len [string length $h3d_path]
    set model_name [string range $h3d_path 0 [expr $len - 5]]
    puts $subcase_idx
    puts $result_name
    set suffix [format "subcase%02d-%s" $subcase_idx $result_name]
    set csv_path "$model_name-$suffix.csv"

    # Export
    hwi GetSessionHandle sess
    sess GetClientManagerHandle pm Plot
    pm GetExportCtrlHandle exp
    exp SetFormat "CSV Blocks"
    exp SetFilename $csv_path
    exp Export

    # Release
    hwc xy curve delete range=$range_window
    sess ReleaseHandle
    pm ReleaseHandle
    exp ReleaseHandle
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
    # Configuratons
    if {[lindex $argv 1] == "-tcl"} {
        lassign [lrange $argv 3 end] h3d_path nodes subcase_indices result_types result_components result_names
        set subcase_indices [split $subcase_indices ","]
        set result_types [split $result_types ","]
        set result_components [split $result_components ","]
        set result_names [split $result_names ","]
        set exit "true"
    } else {
        set h3d_path [get_current_file_name]
        # set nodes "2357428,2357684,2328963,2325886";  # 8 modules
        set nodes "2326131,2325886,2357683,2357432";  # 7 modules
        set exit "false"
        set subcase_indices "2 3 4"
        set result_types {"Acceleration (Grids)"  "Acceleration (Grids)" "Acceleration (Grids)"}
        set result_components {"MAG | X" "MAG | Y" "MAG | Z"}
        set result_names "accX accY accZ"
    }
    set h3d_path [string map {\\ /} $h3d_path]
    set nodes [split $nodes ","]
    set page_idx "1"
    set window_idx "2"
    set range_window "p:$page_idx w:$window_idx"

    for {set i 0} {$i < [llength $subcase_indices]} {incr i} {
        set subcase_idx [lindex $subcase_indices $i]
        set result_type [lindex $result_types $i]
        set result_comp [lindex $result_components $i]
        set result_name [lindex $result_names $i]

        # Manipulate the page and windows
        hwc open animation modelandresult $h3d_path $h3d_path
        hwc hwd page current layout=1 activewindow=$window_idx
        hwc hwd window type="HyperGraph 2D"
        create_curves $range_window $h3d_path $subcase_idx $nodes $result_type $result_comp

        # Export and exit
        export_csv $h3d_path $range_window $subcase_idx $result_name
    }

    if {$exit} {
        hwc hwd exit
    }
}


main $argv

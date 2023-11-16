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
    set model_name [string trimright $h3d_path ".h3d"]
    set suffix "subcase2"
    set csv_path "$model_name-$suffix.csv"

    hwi GetSessionHandle sess
    sess GetClientManagerHandle pm Plot
    pm GetExportCtrlHandle exp
    exp SetFormat "CSV Blocks"
    exp SetFilename $csv_path
    exp Export
}


proc main {argv} {
    # Parse arguments
    lassign [lrange $argv 3 end] arg_1 arg_2
    set h3d_path [string map {\\ /} $arg_1]
    set nodes [split $arg_2 ","]

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
    hwc hwd exit
}


main $argv

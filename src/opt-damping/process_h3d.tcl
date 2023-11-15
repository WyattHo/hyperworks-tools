# Parse arguments
lassign [lrange $argv 3 end] arg_1 arg_2
set file_h3d [string map {\\ /} $arg_1]
set nodes [split $arg_2 ","]


# Open h3d
hwc open animation modelandresult $file_h3d $file_h3d


# Modify the page and windows
hwc hwd page current layout=1 activewindow=2
hwc hwd window type="HyperGraph 2D"


set line_idx 0
foreach node_idx $nodes {
    set line_idx [expr $line_idx + 1]
    set node_label "N$node_idx"

    # Create empty curve
    set page "1"
    set window "2"
    set subcase "Subcase 2 (FRF_X)"
    set range_window "p:$page w:$window"
    set range_curve "p:$page w:$window i:$line_idx"
    hwc xy curve create range=$range_window

    # Edit X data
    hwc xy curve edit range=$range_curve xfile=$file_h3d
    hwc xy curve edit range=$range_curve xsubcase=$subcase
    hwc xy curve edit range=$range_curve xtype="Acceleration (Grids)"
    hwc xy curve edit range=$range_curve xrequest=$node_label
    hwc xy curve edit range=$range_curve xcomponent="Time"

    # Edit Y data
    hwc xy curve edit range=$range_curve yfile=$file_h3d
    hwc xy curve edit range=$range_curve ysubcase=$subcase
    hwc xy curve edit range=$range_curve ytype="Acceleration (Grids)"
    hwc xy curve edit range=$range_curve yrequest=$node_label
    hwc xy curve edit range=$range_curve ycomponent="MAG | X"
}


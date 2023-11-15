# Open h3d
set file_h3d "D:/my-analysis/kubota-package-8-module/test/kbt-fully-customized-8-module-un383.h3d"
hwc open animation modelandresult $file_h3d $file_h3d


# Modify the page and windows
hwc hwd page current layout=1 activewindow=2
hwc hwd window type="HyperGraph 2D"

# Create empty curve
set page "1"
set window "2"
set line "1"
set node "N2357683"
set subcase "Subcase 2 (FRF_X)"
set range_window "p:$page w:$window"
set range_curve "p:$page w:$window i:$line"
hwc xy curve create range=$range_window

# Edit X data
hwc xy curve edit range=$range_curve xfile=$file_h3d
hwc xy curve edit range=$range_curve xsubcase=$subcase
hwc xy curve edit range=$range_curve xtype="Acceleration (Grids)"
hwc xy curve edit range=$range_curve xrequest=$node
hwc xy curve edit range=$range_curve xcomponent="Time"

# Edit Y data
hwc xy curve edit range=$range_curve yfile=$file_h3d
hwc xy curve edit range=$range_curve ysubcase=$subcase
hwc xy curve edit range=$range_curve ytype="Acceleration (Grids)"
hwc xy curve edit range=$range_curve yrequest=$node
hwc xy curve edit range=$range_curve ycomponent="MAG | X"


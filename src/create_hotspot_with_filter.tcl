# configurations
set result_type "Element Stresses (2D & 3D)"
set filter_value 245
set hotspot_label "Hotspot Query 1"
set num_hotspot 2
set lower_value 0
set component_indices "1 2 4 5 6 7"


# show target components only
hwc hide component all
foreach idx $component_indices {
    hwc show component $idx
}


# initial
hwc animate mode static
hwc result scalar load type=$result_type
hwc kpi hotspot clear


# hotspot settings
hwc kpi hotspot create $hotspot_label
hwc kpi hotspot $hotspot_label criteria loadcase=current filtertype=greaterthan lowervalue=$lower_value minimumdistance=75.000000 numberofhotspottype=top numberofhotpottopvalue=$num_hotspot
hwc kpi hotspot $hotspot_label findhotspots


# filter the contour and create hotspot
hwc result scalar load type=$result_type filtermode=below filtervalue=$filter_value
hwc kpi hotspot $hotspot_label findhotspots
hwc kpi hotspot $hotspot_label review

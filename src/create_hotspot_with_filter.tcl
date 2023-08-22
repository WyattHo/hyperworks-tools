# configurations
set result_type "Element Stresses (2D & 3D)"
set filter_value 245
set hotspot_label "Hotspot Query 1"
set num_hotspot 2
set lower_value 0
set component_indices "1 2 4 5 6 7"
set legend_format fixed
set legend_precision 1
set deform_scale 1.0


# show target components only
hwc hide component all
foreach idx $component_indices {
    hwc show component $idx
}


# initial
hwc animate mode static
hwc result scalar clear
hwc result scalar load type=$result_type filtermode=none filtervalue=20 avgmode=advanced;  # filtervalue is necessary. wtf..
hwc kpi hotspot clear


# legend settings
hwc result scalar legend layout format=$legend_format
hwc result scalar legend layout precision=$legend_precision
hwc result scalar legend values maximum=false
hwc result scalar legend values minimum=false


# hotspot settings
hwc kpi hotspot create $hotspot_label
hwc kpi hotspot $hotspot_label criteria loadcase=current filtertype=greaterthan lowervalue=$lower_value minimumdistance=75.000000 numberofhotspottype=top numberofhotpottopvalue=$num_hotspot
hwc kpi hotspot $hotspot_label findhotspots


# filter the contour and create hotspot
hwc result scalar load type=$result_type filtermode=below filtervalue=$filter_value
hwc kpi hotspot $hotspot_label findhotspots
hwc kpi hotspot $hotspot_label review


# show target components only
hwc hide component all
foreach idx $component_indices {
    hwc show component $idx
}


# misc. settings
hwc scale deformed resulttype=Displacement value=$deform_scale
hwc hide note "Model Info"

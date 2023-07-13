proc create_list_filled_with_value {length val} {
    set answer ""
    for {set i 0} {$i < $length} {incr i} {
        lappend answer $val
    }
    return $answer
}


proc create_line_list {line_indices} {
    set answer line
    foreach idx $line_indices {
        lappend answer $idx
    }
    return $answer
}


# Select the target surface
*createmarkpanel surfs 1 "Please select the target surface.."

# Returns surface and element free and non-manifold edge loop entities.
set loops [hm_getedgeloops surfs markid=1]
## {128 6181 8930 6181} {128 6183 8929 6183} {128 6185 8928 6185}, ...
## {type line-id line-id line-id}
## The first value in each loop list is the loop type.
## The remaining values are the ordered node/surface edge IDs defining the loop.
## If the loop is closed, the first and last ID are the same.

# Get nodes on each loop lines
foreach loop_data $loops {
    # Parameters for the while loop
    set idx 2
    set data_len [llength $loop_data]
    set idx_end [expr $data_len - 1]
    set line_indices [lindex $loop_data 1]

    # Collect line indices for each line loop
    while {$idx < $idx_end} {
        lappend line_indices [lindex $loop_data $idx]
        incr idx 1
    }

    # Collect nodes for each line loop
    set looplines [create_line_list $line_indices]
    set node_indices [hm_getgeometrynodes $looplines node_query=points]

    # Analyze the area of the line loop
    eval *createmark nodes 1 $node_indices
    set bbox [hm_getboundingbox nodes 1 0 0 0]
    set x_min [lindex $bbox 0]
    set y_min [lindex $bbox 1]
    set x_max [lindex $bbox 3]
    set y_max [lindex $bbox 4]
    set area [expr ($x_max - $x_min) * ($y_max - $y_min)]
    set area_min [expr 0.8 * 0.015 * 0.015]
    set area_max [expr 1.5 * 0.015 * 0.015]

    # Create RBE3
    if {$area > $area_min & $area < $area_max} {
        set node_num [llength $node_indices]
        set dofs [create_list_filled_with_value $node_num 123]
        set weights [create_list_filled_with_value $node_num 1]
        eval *createarray 23 $dofs
        eval *createdoublearray 23 $weights
        eval *rbe3 1 1 $node_num 1 $node_num 0 123456 1
    }

    *clearmark nodes 1
}
puts "Done!"

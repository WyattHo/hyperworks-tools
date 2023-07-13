proc create_list_filled_with_value {length val} {
    set answer ""
    for {set i 0} {$i < $length} {incr i} {
        lappend answer $val
    }
    return $answer
}


proc extrac_line_indices {loop_data} {
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
    return $line_indices
}


proc create_line_list {line_indices} {
    set answer line
    foreach idx $line_indices {
        lappend answer $idx
    }
    return $answer
}


proc extrac_node_indices {line_indices} {
    # Collect nodes for each line loop
    set looplines [create_line_list $line_indices]
    set node_indices [hm_getgeometrynodes $looplines node_query=points]
    set node_num [llength $node_indices]
    if {$node_num == 0} {
        set node_indices [hm_getgeometrynodes $looplines node_query=points query_type=fegeometry]
    }
    return $node_indices
}


# Select the target surface
*createmarkpanel surfs 1 "Please select the target surface.."

# Input the target dimension
set dimension_x [hm_getstring "Dimension in x direction: " "Please enter.."]
set dimension_y [hm_getstring "Dimension in y direction: " "Please enter.."]

# Returns surface and element free and non-manifold edge loop entities.
set loops [hm_getedgeloops surfs markid=1]
## {128 6181 8930 6181} {128 6183 8929 6183} {128 6185 8928 6185}, ...
## {type line-id line-id line-id}
## The first value in each loop list is the loop type.
## The remaining values are the ordered node/surface edge IDs defining the loop.
## If the loop is closed, the first and last ID are the same.

# Get nodes on each loop lines
set tgt_loop_count 0
foreach loop_data $loops {
    set line_indices [extrac_line_indices $loop_data]
    set node_indices [extrac_node_indices $line_indices]

    # Analyze the area of the line loop
    eval *createmark nodes 1 $node_indices
    set bbox [hm_getboundingbox nodes 1 0 0 0]
    set x_min [lindex $bbox 0]
    set y_min [lindex $bbox 1]
    set x_max [lindex $bbox 3]
    set y_max [lindex $bbox 4]
    
    set delta_x [expr $x_max - $x_min]
    set delta_x_min [expr 0.9 * $dimension_x]
    set delta_x_max [expr 1.1 * $dimension_x]
    
    set delta_y [expr $y_max - $y_min]
    set delta_y_min [expr 0.9 * $dimension_y]
    set delta_y_max [expr 1.1 * $dimension_y]

    # Create RBE3
    if {$delta_x > $delta_x_min & $delta_x < $delta_x_max & $delta_y > $delta_y_min & $delta_y < $delta_y_max} {
        incr tgt_loop_count 1
        set node_num [llength $node_indices]
        set dofs [create_list_filled_with_value $node_num 123]
        set weights [create_list_filled_with_value $node_num 1]
        eval *createarray 23 $dofs
        eval *createdoublearray 23 $weights
        eval *rbe3 1 1 $node_num 1 $node_num 0 123456 1
    }
    *clearmark nodes 1
}
puts "Done! Created $tgt_loop_count RBE3s."

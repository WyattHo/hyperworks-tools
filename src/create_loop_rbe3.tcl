proc extrac_line_indices {loop_data} {
    # Parameters for the while loop
    set idx 2
    set data_len [llength $loop_data]
    set idx_end [expr $data_len - 1]
    set line_indices [lindex $loop_data 1]

    # Collect line indices
    while {$idx < $idx_end} {
        lappend line_indices [lindex $loop_data $idx]
        incr idx 1
    }
    return $line_indices
}


proc extrac_node_indices {line_indices} {
    # Collect nodes for each line loop
    set line_list [linsert $line_indices 0 line]
    set node_indices [hm_getgeometrynodes $line_list node_query=points]
    set node_num [llength $node_indices]
    if {$node_num == 0} {
        set node_indices [hm_getgeometrynodes $line_list node_query=points query_type=fegeometry]
    }
    return $node_indices
}


proc check_target {mark_id dimension_x dimension_y} {
    set bbox [hm_getboundingbox nodes $mark_id 0 0 0]
    set x_min [lindex $bbox 0]
    set y_min [lindex $bbox 1]
    set x_max [lindex $bbox 3]
    set y_max [lindex $bbox 4]
    set delta_x [expr $x_max - $x_min]
    set delta_y [expr $y_max - $y_min]
    set delta_x_min [expr 0.9 * $dimension_x]
    set delta_x_max [expr 1.1 * $dimension_x]
    set delta_y_min [expr 0.9 * $dimension_y]
    set delta_y_max [expr 1.1 * $dimension_y]
    set is_target [expr $delta_x > $delta_x_min & $delta_x < $delta_x_max & $delta_y > $delta_y_min & $delta_y < $delta_y_max]
    return $is_target
}


proc create_list_filled_with_value {length val} {
    set answer ""
    for {set i 0} {$i < $length} {incr i} {
        lappend answer $val
    }
    return $answer
}


proc create_rbe3 {mark_id node_indices} {
    set node_num [llength $node_indices]
    set dofs [create_list_filled_with_value $node_num 123]
    set weights [create_list_filled_with_value $node_num 1]
    eval *createarray 23 $dofs
    eval *createdoublearray 23 $weights
    eval *rbe3 $mark_id 1 $node_num 1 $node_num 0 123456 1
}


proc main {} {
    *createmarkpanel surfs 1 "Please select the target surface.."
    set dimension_x [hm_getstring "Dimension in x direction: " "Please enter.."]
    set dimension_y [hm_getstring "Dimension in y direction: " "Please enter.."]
    set loops [hm_getedgeloops surfs markid=1]
    set tgt_loop_count 0
    foreach loop_data $loops {
        set line_indices [extrac_line_indices $loop_data]
        set node_indices [extrac_node_indices $line_indices]
        set mark_id 1
        eval *createmark nodes $mark_id $node_indices
        set is_target [check_target $mark_id $dimension_x $dimension_y]
        if {$is_target} {
            incr tgt_loop_count 1
            create_rbe3 $mark_id $node_indices
        }
        *clearmark nodes $mark_id
    }
    puts "Done! Created $tgt_loop_count RBE3s."
}

main

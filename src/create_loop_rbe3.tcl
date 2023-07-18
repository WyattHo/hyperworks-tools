# extrac_line_indices --
#
#   The first value in each loop data is the loop type.
#   The remaining values are the ordered line IDs defining the loop.
#   If the loop is closed, the first and last ID are the same.
#   This function extrac only the values of unique line IDs.
# ...
proc extrac_line_indices {loop_data} {
    set idx_str 1
    set data_len [llength $loop_data]
    set idx_end [expr $data_len - 1]
    set line_indices [lrange $loop_data $idx_str $idx_end]
    return $line_indices
}


proc extrac_node_indices {line_indices} {
    set line_list [linsert $line_indices 0 line]
    set node_indices [hm_getgeometrynodes $line_list node_query=points]
    set node_num [llength $node_indices]
    if {$node_num == 0} {
        set node_indices [hm_getgeometrynodes $line_list node_query=points query_type=fegeometry]
    }
    return $node_indices
}


proc check_target {markid_nodes dimension_x dimension_y} {
    set bbox [hm_getboundingbox nodes $markid_nodes 0 0 0]
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
    set is_target [expr ($delta_x > $delta_x_min)\
                        && ($delta_x < $delta_x_max)\
                        && ($delta_y > $delta_y_min)\
                        && ($delta_y < $delta_y_max)]
    return $is_target
}


proc create_rbe3 {markid_nodes node_indices} {
    set node_num [llength $node_indices]
    set dofs [lrepeat $node_num 123]
    set weights [lrepeat $node_num 1]
    eval *createarray $node_num $dofs
    eval *createdoublearray $node_num $weights
    eval *rbe3 $markid_nodes 1 $node_num 1 $node_num 0 123456 1
}


proc main {} {
    set markid_surfs 1
    *createmarkpanel surfs $markid_surfs "Please select the target surface.."
    set dimension_x [hm_getstring "Dimension in x direction: " "Please enter.."]
    set dimension_y [hm_getstring "Dimension in y direction: " "Please enter.."]
    set loops_data [hm_getedgeloops surfs markid=$markid_surfs]
    set tgt_loop_count 0
    foreach loop_data $loops_data {
        set line_indices [extrac_line_indices $loop_data]
        set node_indices [extrac_node_indices $line_indices]
        set markid_nodes 1
        eval *createmark nodes $markid_nodes $node_indices
        set is_target [check_target $markid_nodes $dimension_x $dimension_y]
        if {$is_target} {
            incr tgt_loop_count 1
            create_rbe3 $markid_nodes $node_indices
        }
        *clearmark nodes $markid_nodes
    }
    puts "Done! Created $tgt_loop_count RBE3s."
}


main

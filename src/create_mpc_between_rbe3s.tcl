proc get_dependent_nodes {elem_indices} {
    set dependent_nodes {}
    foreach elem_idx $elem_indices {
        lappend dependent_nodes [hm_getvalue element id=$elem_idx dataname=dependentnode]
    }
    return $dependent_nodes
}


proc sort_nodes_in_z {node_pair} {
    lassign $node_pair node1 node2
    set coordz_1 [lindex [hm_getvalue nodes id=$node1 dataname=coordinates] end]
    set coordz_2 [lindex [hm_getvalue nodes id=$node2 dataname=coordinates] end]
    if {$coordz_1 > $coordz_2} {
        return "$node1 $node2"
    } else {
        return "$node2 $node1"
    }
}


proc find_rbe3_pairs {node_indices} {
    set rbe3_pairs {}
    set already_considered {}
    foreach node_idx_current $node_indices {
        if {$node_idx_current in $already_considered} {
            continue
        }
        set idx_current [lsearch $node_indices $node_idx_current]
        set other_indices [lreplace $node_indices $idx_current $idx_current]
        set distances {}
        foreach node_idx $other_indices {
            lappend distances [lindex [hm_getdistance nodes $node_idx_current $node_idx 0] 0]
        }
        set distance_min [lindex [lsort $distances] 0]
        set idx_closest [lsearch $distances $distance_min]
        set node_idx_closest [lindex $other_indices $idx_closest]
        set node_pair [sort_nodes_in_z "$node_idx_current $node_idx_closest"]
        lappend rbe3_pairs $node_pair
        lappend already_considered $node_idx_current $node_idx_closest
    }
    return $rbe3_pairs
}


proc get_latest_node_id {} {
    set markid_nodes 1
    *createmark nodes $markid_nodes -1
    set latest_node_id [hm_getmark nodes $markid_nodes]
    *clearmark nodes $markid_nodes
    return $latest_node_id
}


proc create_mpc {independent_nodes dependent_node} {
    set markid_nodes 1
    set dof_size [llength $independent_nodes]
    set weight_size [expr 6 * $dof_size]
    eval *createmark nodes $markid_nodes $independent_nodes
    *createarray $dof_size [lrepeat $dof_size 4]
    *createdoublearray $weight_size [lrepeat $weight_size 1.0]
    *equationcreate $markid_nodes 1 $dof_size 1 $weight_size $dependent_node 3 1.0 0.0
    *setvalue equations id=-1 STATUS=2 ROW=0 independentcoeffs3={-1}
    *setvalue equations id=-1 STATUS=2 ROW=1 independentcoeffs3={1}
    *clearmark nodes $markid_nodes
}


proc main {} {
    set markid_elems 1
    *createmarkpanel elems $markid_elems "Please select the target elements.."
    set elem_indices [hm_getmark elems $markid_elems]
    set dependent_nodes [get_dependent_nodes $elem_indices]
    set rbe3_pairs [find_rbe3_pairs $dependent_nodes]
    foreach node_pair $rbe3_pairs {
        lassign $node_pair node1 node2
        eval *createnodesbetweennodes $node1 $node2 1
        set dependent_node [get_latest_node_id]
        create_mpc $node_pair $dependent_node
    }
    *clearmark elems $markid_elems
}


main

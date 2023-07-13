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
    set node_indices [hm_getgeometrynodes [list lines $line_indices] node_query=points]
    puts $node_indices
    
    # Analyze the area of the line loop
    eval *createmark nodes 1 $node_indices
    set bbox [hm_getboundingbox nodes 1 0 0 0]
    set x_min [lindex $bbox 0]
    set y_min [lindex $bbox 1]
    set x_max [lindex $bbox 3]
    set y_max [lindex $bbox 4]
    set area [expr ($x_max - $x_min) * ($y_max - $y_min)]
    set area_criteria 400

    # # Create RBE3
    # if {$area < $area_criteria} {
    #     puts $area
    # }
}


# *createmark nodes 2 5493161 5493160 5493159 5493158 5493157 5493156 5493155 \
#     5493154 5493153 5493152 5493151 5479208 5479207 5479206 5479205 5479204 5479203 \
#     5479202 5479201 5479200 5479199 5479198 5479197
# *createarray 23 123 123 123 123 123 123 123 123 123 123 123 123 123 123 123 \
#     123 123 123 123 123 123 123 123
# *createdoublearray 23 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
# *rbe3 2 1 23 1 23 0 123456 1
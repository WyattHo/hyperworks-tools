proc save_viewpoint {} {
    hwi OpenStack
    hwi GetSessionHandle session_handle
    session_handle GetProjectHandle project_handle
    project_handle GetPageHandle page_handle [project_handle GetActivePage]
    page_handle GetWindowHandle window_handle [page_handle GetActiveWindow]
    window_handle GetClientHandle client_handle
    window_handle GetViewControlHandle viewctrl_handle
    set orientation [viewctrl_handle GetOrientation "Current View"]
    set ortho [viewctrl_handle GetOrtho "Current View"]
    puts "save orientation: $orientation"
    puts "save ortho: $ortho"
    hwi CloseStack
    return "$orientation $ortho"
}

proc reproduce_viewpoint {} {
    global viewpoint
    set orientation [lrange $viewpoint 0 5]
    set ortho [lrange $viewpoint 6 end]
    puts "reproduce orientation: $orientation"
    puts "reproduce ortho: $ortho"
    hwi OpenStack
    hwi GetSessionHandle session_handle
    session_handle GetProjectHandle project_handle
    project_handle GetPageHandle page_handle [project_handle GetActivePage]
    page_handle GetWindowHandle window_handle [page_handle GetActiveWindow]
    window_handle GetClientHandle client_handle
    window_handle GetViewControlHandle viewctrl_handle
    viewctrl_handle SetOrientation "$orientation" "Current View"
    viewctrl_handle SetOrtho "$ortho" "Current View"
    hwi CloseStack
}

proc retValues {} {return "save reproduce"}

proc main {} {
    # Reference of "hwtk::inputdialog"
    # https://2021.help.altair.com/2021/hwsolvers/altair_help/topics/reference/hwtk/hwtk_inputdialog.htm
    set mode [\
        ::hwtk::inputdialog \
            -title "Viewpoint: " \
            -text "Choose the mode:" \
            -inputtype "combobox" \
            -valuelistcommand retValues]

    global viewpoint
    if {[string match save $mode]} {
        set viewpoint [save_viewpoint]
    } else {
        reproduce_viewpoint
    }
    puts "-----------Done!-----------"
}
main


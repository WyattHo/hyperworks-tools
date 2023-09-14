hwi OpenStack
hwi GetSessionHandle session_handle
session_handle GetProjectHandle project_handle
project_handle GetPageHandle page_handle [project_handle GetActivePage]
page_handle GetWindowHandle window_handle [page_handle GetActiveWindow]
window_handle GetClientHandle client_handle
window_handle GetViewControlHandle viewctrl_handle
set orientation [viewctrl_handle GetOrientation]
set ortho [viewctrl_handle GetOrtho]
hwi CloseStack

###

hwi OpenStack
hwi GetSessionHandle session_handle
session_handle GetProjectHandle project_handle
project_handle GetPageHandle page_handle [project_handle GetActivePage]
page_handle GetWindowHandle window_handle [page_handle GetActiveWindow]
window_handle GetClientHandle client_handle
window_handle GetViewControlHandle viewctrl_handle
viewctrl_handle SetOrientation "$orientation"
viewctrl_handle SetOrtho "$ortho"
hwi CloseStack

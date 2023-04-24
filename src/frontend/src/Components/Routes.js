import {
    Route,
    Routes as Switch,
    useLocation,
    matchPath
} from "react-router-dom"
import Home from '../Pages/Home'
import SignIn from '../Pages/SignIn'
import Register from '../Pages/Register'
import RegisterWithIdCard from '../Pages/RegisterWithIdCard'
import Success from '../Pages/Success'
import LoggedIn from '../Pages/LoggedIn'
import { useEffect } from "react"
import {
    useAppLayoutDispatch,
    useAppLayoutContext
} from "./context/AppLayoutContext"

export const routes = [
    {
        path: "/",
        element: <Home />,
        exact: true,
        contentType: "default",
        navigationHide: true

    },
    {
        path: "/login",
        element: <SignIn />,
        exact: true,
        contentType: "default",
        navigationHide: true
      },
      {
        path: "/register",
        element: <Register/>,
        exact: true,
        contentType: "default",
        navigationHide: true
      },
      {
        path: "/registerwithid",
        element: <RegisterWithIdCard/>,
        exact: true,
        contentType: "default",
        navigationHide: true
      },
      {
        path: "/success",
        element: <Success/>,
        exact: true,
        contentType: "default",
        navigationHide: true
      },
      {
        path: "/loggedin",
        element: <LoggedIn/>,
        exact: true,
        contentType: "default",
        navigationHide: true
      }


]

const Routes = () => {
    const { pathname } = useLocation()
    const { setContentType } = useAppLayoutDispatch()
    const { state } = useAppLayoutContext()

    useEffect(() => {
        const currentRoute = routes.find((i) => matchPath(i.path, pathname))
        const newContentType = currentRoute?.contentType || "default"
        const newNavHide = currentRoute?.navigationHide
        if (newContentType !== state.contentType || newNavHide !== state.navigationHide) {
            setContentType(currentRoute?.contentType || "default", currentRoute?.navigationHide)
        }
    }, [pathname, setContentType, state.contentType, state.navigationHide])

    return (
        <Switch>
            {routes.map(({ contentType, ...route }, i) => (
                <Route key={i} {...route} />
            ))}
            <Route path="*" element={<Home />} />
        </Switch>
    )
}

export default Routes


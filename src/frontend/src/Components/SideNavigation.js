import { SideNavigation as Navigation } from "@awsui/components-react"
import { useSideNavigation } from "use-awsui-router"
import { API } from "aws-amplify";
import {
  useNavigate
} from "react-router-dom";
import { Button } from '@aws-amplify/ui-react';
let MAIN_ITEMS = [{ type: "link", text: "Login", href: "/login" },
{ type: "link", text: "Register", href: "/register" },
{ type: "link", text: "Register with ID", href: "/registerwithid" }
// { type: "link", text: "Delete all users", href: "#", onclick: "deleteUsers()" }
]

const FOOTER_ITEMS = [
  { type: "divider" },
  {
    type: "link",
    text: "Documentation",
    href: "https://aws.amazon.com/rekognition/identity-verification/",
    external: true
  }
]

const SideNavigation = () => {

  const navigate = useNavigate();
  function deleteUsers() {
    console.log('User deleted')
    const options = { headers: {
      'Content-Type': 'application/json'
    }}
    API.get("identityverification", "reset-user", options).then(response => {
        // localStorage.removeItem("pic");
        navigate("/");
     });
  }
  const { activeHref, handleFollow } = useSideNavigation()
  let items = [...MAIN_ITEMS]

  items.push(...FOOTER_ITEMS)

  return (
    <>
      <Navigation
        header={{ href: "/", text: "Try Out" }}
        activeHref={activeHref.split("?")[0]}
        items={items}
        onFollow={handleFollow}
  />

        <Button onClick={deleteUsers} variation="primary" marginLeft={'20px'} >
        Delete all users
        </Button>
   
    </>
  )
}

export default SideNavigation

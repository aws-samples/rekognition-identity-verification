import { createContext, useContext, useReducer, useMemo } from "react"

const initialAppLayout = {
  contentType: "default",
  navigationHide:false
}

export const AppLayoutContext = createContext({
  state: initialAppLayout
})

const reducer = (state, action) => {
  switch (action.type) {
    case "SET_CONTENT_TYPE":
      return {
        ...state,
        contentType: action.payload.contentType || initialAppLayout.contentType,
        navigationHide:action.payload.navigationHide || initialAppLayout.navigationHide
      }
    default:
      throw new Error(`Unknown action type: ${action.type}`)
  }
}

export const useAppLayoutDispatch = () => {
  const { dispatch } = useContext(AppLayoutContext)
  return {
    setContentType: (contentType,navigationHide) =>
      dispatch({
        type: "SET_CONTENT_TYPE",
        payload: {
          contentType,
          navigationHide
        }
      })
  }
}

export const AppLayoutProvider = (props) => {
  const [state, dispatch] = useReducer(reducer, initialAppLayout, (arg) => arg)
  const contextValue = useMemo(() => {
    return { state, dispatch }
  }, [state, dispatch])

  return (
    <AppLayoutContext.Provider value={contextValue}>
      {props.children}
    </AppLayoutContext.Provider>
  )
}

export const useAppLayoutContext = () => useContext(AppLayoutContext)

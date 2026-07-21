import {
  Navigate,
  createBrowserRouter,
} from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { NotFoundPage } from "../pages/NotFoundPage";
import { SettingsPage } from "../pages/SettingsPage";
import { TodosPage } from "../pages/TodosPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: (
          <Navigate
            to="/todos"
            replace
          />
        ),
      },
      {
        path: "todos",
        element: <TodosPage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);
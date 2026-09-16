import { createBrowserRouter } from "react-router-dom";

import { Shell } from "@/components/layout/Shell";
import HomePage from "@/pages/store/HomePage";
import ProductPage from "@/pages/store/ProductPage";
import ShopPage from "@/pages/store/ShopPage";

export const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/shop", element: <ShopPage /> },
      { path: "/product/:slug", element: <ProductPage /> },
    ],
  },
]);

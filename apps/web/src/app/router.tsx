import { createBrowserRouter } from "react-router-dom";

import { Shell } from "@/components/layout/Shell";
import ConceptDetailPage from "@/features/reality/pages/ConceptDetailPage";
import ConceptsPage from "@/features/reality/pages/ConceptsPage";
import RealityHomePage from "@/features/reality/pages/RealityHomePage";
import TopicDetailPage from "@/features/reality/pages/TopicDetailPage";
import TopicsPage from "@/features/reality/pages/TopicsPage";
import HomePage from "@/pages/store/HomePage";
import CheckoutPage from "@/pages/store/CheckoutPage";
import ProductPage from "@/pages/store/ProductPage";
import ShopPage from "@/pages/store/ShopPage";

export const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/shop", element: <ShopPage /> },
      { path: "/product/:slug", element: <ProductPage /> },
      { path: "/checkout", element: <CheckoutPage /> },
      { path: "/reality", element: <RealityHomePage /> },
      { path: "/reality/topics", element: <TopicsPage /> },
      { path: "/reality/topics/:slug", element: <TopicDetailPage /> },
      { path: "/reality/concepts", element: <ConceptsPage /> },
      { path: "/reality/concepts/:slug", element: <ConceptDetailPage /> },
    ],
  },
]);

import { createBrowserRouter } from "react-router-dom";

import { Shell } from "@/components/layout/Shell";
import ConceptDetailPage from "@/features/reality/pages/ConceptDetailPage";
import ConceptsPage from "@/features/reality/pages/ConceptsPage";
import RealityHomePage from "@/features/reality/pages/RealityHomePage";
import TopicDetailPage from "@/features/reality/pages/TopicDetailPage";
import TopicsPage from "@/features/reality/pages/TopicsPage";
import CheckoutPage from "@/pages/store/CheckoutPage";
import HomePage from "@/pages/store/HomePage";
import WishlistPage from "@/pages/store/WishlistPage";
import NotFoundPage from "@/pages/NotFoundPage";
import ProductPage from "@/pages/store/ProductPage";
import ShopPage from "@/pages/store/ShopPage";
import PrivacyPolicyPage from "@/pages/legal/PrivacyPolicyPage";
import TermsOfServicePage from "@/pages/legal/TermsOfServicePage";
import { legalRoutes } from "@/app/legalRoutes";
import SignUpPage from "@/pages/account/SignUpPage";
import SignInPage from "@/pages/account/SignInPage";
import AccountPage from "@/pages/account/AccountPage";
import ShippingProfilePage from "@/pages/account/ShippingProfilePage";

export const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/shop", element: <ShopPage /> },
      { path: "/product/:slug", element: <ProductPage /> },
      { path: "/checkout", element: <CheckoutPage /> },
      { path: "/sign-up/*", element: <SignUpPage /> },
      { path: "/sign-in/*", element: <SignInPage /> },
      { path: "/account", element: <AccountPage /> },
      { path: "/account/setup", element: <ShippingProfilePage /> },
      { path: "/wishlist", element: <WishlistPage /> },
      { path: legalRoutes.privacy, element: <PrivacyPolicyPage /> },
      { path: legalRoutes.terms, element: <TermsOfServicePage /> },
      { path: "/reality", element: <RealityHomePage /> },
      { path: "/reality/topics", element: <TopicsPage /> },
      { path: "/reality/topics/:slug", element: <TopicDetailPage /> },
      { path: "/reality/concepts", element: <ConceptsPage /> },
      { path: "/reality/concepts/:slug", element: <ConceptDetailPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);

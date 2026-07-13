<script setup>
import { provide } from "vue";
import { useRouter } from "vue-router";

import App from "./App.vue";
import LoginPage from "@/pages/LoginPage.vue";

const props = defineProps({ session: { type: Object, required: true }, branding: { type: Object, default: () => ({}) } });
const router = useRouter();
provide("retailSession", props.session);
provide("retailBranding", props.branding);

async function afterLogin() {
  const returnTo = new URLSearchParams(window.location.search).get("return_to") || "";
  const requested = window.location.pathname.startsWith("/retail-erp/")
    ? window.location.pathname + window.location.search
    : returnTo.startsWith("/retail-erp/") ? returnTo : props.session.state.landingRoute;
  const authorization = await props.session.authorize(requested);
  const target = authorization.outcome === "allowed" ? requested : authorization.route || props.session.state.landingRoute;
  await router.replace(target.replace(/^\/retail-erp/, "") || "/home");
}
</script>

<template>
  <LoginPage v-if="!session.state.authenticated" :session="session" :branding="branding" @authenticated="afterLogin" />
  <App v-else :context="{ standalone: true }" />
</template>

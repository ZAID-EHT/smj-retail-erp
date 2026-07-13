<script setup>
import { computed, ref } from "vue";

const props = defineProps({ session: { type: Object, required: true }, branding: { type: Object, default: () => ({}) } });
const emit = defineEmits(["authenticated"]);
const username = ref("");
const password = ref("");
const otp = ref("");
const showPassword = ref(false);
const loading = ref(false);
const error = ref("");
const twoFactor = ref(null);
const forgotMode = ref(false);
const resetSent = ref(false);

const companyName = computed(() => props.branding.brand || "Retail ERP");

async function submit() {
  error.value = "";
  if (forgotMode.value) {
    if (!username.value.trim()) { error.value = "Email is required."; return; }
  } else if (twoFactor.value) {
    if (!otp.value.trim()) { error.value = "Verification code is required."; return; }
  } else if (!username.value.trim() || !password.value) {
    error.value = "Username and password are required.";
    return;
  }
  loading.value = true;
  try {
    if (forgotMode.value) {
      await props.session.requestPasswordReset(username.value.trim());
      resetSent.value = true;
      return;
    }
    const result = await props.session.login({
      username: username.value.trim(),
      password: password.value,
      otp: otp.value.trim(),
      tmpId: twoFactor.value?.tmpId,
    });
    if (result.twoFactor) {
      twoFactor.value = result;
      otp.value = "";
      return;
    }
    password.value = "";
    emit("authenticated");
  } catch (_error) {
    error.value = "Sign in failed. Check your credentials or verification code and try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main id="retail-erp-main" class="ref-login-page">
    <section class="ref-login-card" aria-labelledby="login-title">
      <div class="ref-login-brand">
        <img v-if="branding.logo" :src="branding.logo" alt="" />
        <span v-else aria-hidden="true">E</span>
        <div><strong>{{ companyName }}</strong><small>Retail ERP</small></div>
      </div>
      <div class="ref-login-copy">
        <span>SECURE BUSINESS ACCESS</span>
        <h1 id="login-title">{{ forgotMode ? "Reset your password" : twoFactor ? "Verify your sign in" : "Welcome back" }}</h1>
        <p>{{ forgotMode ? "Enter your account email. If it is eligible, password-reset instructions will be sent." : twoFactor ? "Enter the verification code generated or sent for this account." : "Sign in to continue to your role-based workspace." }}</p>
      </div>
      <form novalidate @submit.prevent="submit">
        <label v-if="!twoFactor" for="retail-login-user">{{ forgotMode ? "Email" : "Username or email" }}</label>
        <input v-if="!twoFactor" id="retail-login-user" v-model="username" autocomplete="username" inputmode="email" autofocus />
        <label v-if="!twoFactor && !forgotMode" for="retail-login-password">Password</label>
        <div v-if="!twoFactor && !forgotMode" class="ref-password-field">
          <input id="retail-login-password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" />
          <button type="button" :aria-label="showPassword ? 'Hide password' : 'Show password'" @click="showPassword = !showPassword">{{ showPassword ? "Hide" : "Show" }}</button>
        </div>
        <label v-if="twoFactor" for="retail-login-otp">Verification code</label>
        <input v-if="twoFactor" id="retail-login-otp" v-model="otp" autocomplete="one-time-code" inputmode="numeric" autofocus />
        <p v-if="error" class="ref-login-error" role="alert">{{ error }}</p>
        <p v-else-if="resetSent" class="ref-login-warning" role="status">If the account is eligible, password-reset instructions have been sent.</p>
        <p v-else-if="session.state.expired" class="ref-login-warning" role="status">Your session expired. Sign in again to continue.</p>
        <button class="ref-button ref-button--primary ref-login-submit" type="submit" :disabled="loading">
          {{ loading ? (forgotMode ? "Sending…" : "Signing in…") : forgotMode ? "Send Reset Instructions" : twoFactor ? "Verify" : "Sign In" }}
        </button>
        <button v-if="twoFactor" class="ref-login-secondary" type="button" @click="twoFactor = null; otp = ''; error = ''">Use another account</button>
        <button v-else class="ref-login-forgot" type="button" @click="forgotMode = !forgotMode; resetSent = false; error = ''">{{ forgotMode ? "Back to Sign In" : "Forgot Password?" }}</button>
      </form>
    </section>
  </main>
</template>

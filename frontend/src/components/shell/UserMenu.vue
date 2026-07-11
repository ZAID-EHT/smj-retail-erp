<script setup>
import { computed } from "vue";

const fullName = computed(() => window.frappe?.session?.user_fullname || window.frappe?.session?.user || "User");
const initials = computed(() =>
  fullName.value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "U",
);
</script>

<template>
  <button class="ref-user-menu" type="button" title="User menu placeholder" aria-label="User menu">
    <span class="ref-user-menu__avatar">{{ initials }}</span>
    <span class="ref-user-menu__name">{{ fullName }}</span>
    <span aria-hidden="true">⌄</span>
  </button>
</template>

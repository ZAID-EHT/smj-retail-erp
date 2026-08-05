<script setup>
/* The product image on a card, with the second image reachable when there is one.

   A product carries two image slots. Showing only the first meant the second was
   uploaded and then never seen anywhere, so this slides between whatever the
   product actually has: arrows and dots with a mouse, a swipe on a touch screen,
   arrow keys from the keyboard.

   With one image it renders as a plain picture -- no arrows, no dots, nothing to
   click past -- so a single-image product looks exactly as it did before. */
import { computed, ref, watch } from "vue";

const props = defineProps({
  // Image URLs, in order. Blank entries are dropped, so a product with only the
  // second slot filled still shows that one.
  images: { type: Array, default: () => [] },
  alt: { type: String, default: "" },
  placeholder: { type: String, default: "/assets/my_store_ui/images/product-placeholder.svg" },
  // Stops a click inside the carousel reaching a clickable card behind it, so
  // paging through the images never also adds the product to the cart.
  isolate: { type: Boolean, default: false },
});

const index = ref(0);
const failed = ref(new Set());
let touchStartX = null;

const slides = computed(() => {
  const usable = props.images.filter((url) => typeof url === "string" && url.trim());
  return usable.length ? usable : [props.placeholder];
});
const many = computed(() => slides.value.length > 1);
const current = computed(() => slides.value[Math.min(index.value, slides.value.length - 1)]);

function go(step, event) {
  if (props.isolate && event) event.stopPropagation();
  const total = slides.value.length;
  index.value = (index.value + step + total) % total;
}

function select(position, event) {
  if (props.isolate && event) event.stopPropagation();
  index.value = position;
}

function onTouchStart(event) {
  touchStartX = event.changedTouches?.[0]?.clientX ?? null;
}

function onTouchEnd(event) {
  if (touchStartX === null || !many.value) return;
  const delta = (event.changedTouches?.[0]?.clientX ?? touchStartX) - touchStartX;
  // Short drags are taps, not swipes.
  if (Math.abs(delta) > 40) go(delta < 0 ? 1 : -1, event);
  touchStartX = null;
}

// A broken URL falls back to the placeholder rather than an empty frame, and is
// remembered so the failing request is not repeated on every re-render.
function onError(event) {
  failed.value = new Set(failed.value).add(current.value);
  event.target.src = props.placeholder;
}

// A different product in the same slot starts at its own first image.
watch(() => props.images, () => { index.value = 0; }, { deep: true });
</script>

<template>
  <div
    class="pic"
    :class="{ 'pic--many': many }"
    @touchstart.passive="onTouchStart"
    @touchend.passive="onTouchEnd"
  >
    <img
      :src="current"
      :alt="alt"
      loading="lazy"
      class="pic__image"
      @error="onError"
    />

    <template v-if="many">
      <button
        type="button"
        class="pic__arrow pic__arrow--prev"
        :aria-label="`Previous image of ${alt}`"
        @click="go(-1, $event)"
        @keydown.stop
      >&#8249;</button>
      <button
        type="button"
        class="pic__arrow pic__arrow--next"
        :aria-label="`Next image of ${alt}`"
        @click="go(1, $event)"
        @keydown.stop
      >&#8250;</button>
      <span class="pic__dots">
        <button
          v-for="(slide, position) in slides"
          :key="slide"
          type="button"
          class="pic__dot"
          :class="{ 'is-on': position === index }"
          :aria-label="`Show image ${position + 1} of ${slides.length}`"
          :aria-current="position === index"
          @click="select(position, $event)"
        />
      </span>
    </template>
  </div>
</template>

<style scoped>
.pic{position:relative;display:block;width:100%;overflow:hidden;border-radius:.7rem}
/* `contain` rather than `cover`: a product photo that has been cropped to fill a
   tile is a photo of part of the product, which is not what the picker needs. */
.pic__image{display:block;width:100%;height:100%;object-fit:contain}
.pic__arrow{position:absolute;top:50%;display:flex;align-items:center;justify-content:center;width:28px;height:28px;padding:0;transform:translateY(-50%);border:0;border-radius:50%;background:rgba(15,23,42,.55);color:#fff;font-size:19px;line-height:1;cursor:pointer;opacity:0;transition:opacity .15s ease}
.pic__arrow--prev{left:.35rem}
.pic__arrow--next{right:.35rem}
.pic:hover .pic__arrow,.pic__arrow:focus-visible{opacity:1}
.pic__dots{position:absolute;right:0;bottom:.35rem;left:0;display:flex;justify-content:center;gap:.3rem}
.pic__dot{width:7px;height:7px;padding:0;border:0;border-radius:50%;background:rgba(255,255,255,.6);box-shadow:0 0 0 1px rgba(15,23,42,.35);cursor:pointer}
.pic__dot.is-on{background:#fff;transform:scale(1.25)}
/* Touch devices have no hover, so the arrows stay visible there rather than
   leaving the second image with no way to reach it but a swipe. */
@media (hover:none){
  .pic__arrow{opacity:.85}
}
</style>

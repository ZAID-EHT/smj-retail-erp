<script setup>
/* The product image on a card, with the second image reachable when there is one.

   A product carries two image slots. Showing only the first meant the second was
   uploaded and then never seen anywhere, so this slides between whatever the
   product actually has: arrows and dots with a mouse, a swipe on a touch screen,
   arrow keys from the keyboard.

   Clicking the picture opens it full screen, where the same sliding is available
   at a size worth looking at -- a 136px catalogue tile is enough to recognise a
   rug, not enough to judge one.

   With one image it renders as a plain picture -- no arrows, no dots, nothing to
   click past -- so a single-image product looks exactly as it did before. */
import { computed, onBeforeUnmount, ref, watch } from "vue";

/* The template has two roots (the tile and the teleported viewer), so Vue cannot
   guess which one a caller's `class` belongs to. It belongs to the tile -- that
   is where `.smj-product-images` sets the catalogue tile's height -- so the
   binding is made by hand rather than left to auto-inheritance. */
defineOptions({ inheritAttrs: false });

const props = defineProps({
  // Image URLs, in order. Blank entries are dropped, so a product with only the
  // second slot filled still shows that one.
  images: { type: Array, default: () => [] },
  alt: { type: String, default: "" },
  placeholder: { type: String, default: "/assets/my_store_ui/images/product-placeholder.svg" },
  // Stops a click inside the carousel reaching a clickable card behind it, so
  // paging through the images never also adds the product to the cart.
  isolate: { type: Boolean, default: false },
  // The full-screen viewer. On by default; a caller that wants the picture inert
  // (a dense list row, say) can turn it off.
  zoomable: { type: Boolean, default: true },
});

const index = ref(0);
const failed = ref(new Set());
const zoomed = ref(false);
let touchStartX = null;
// Whatever had focus before the viewer opened, so closing puts it back rather
// than dropping the user at the top of the document.
let opener = null;

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

/* The viewer is a document-level overlay, so it locks the page behind it and
   listens for keys itself. The index is shared with the tile: it opens on the
   image you were looking at, and the tile keeps whatever you paged to. */
function open(event) {
  if (!props.zoomable) return;
  // The card underneath is a button; without this, looking at a product would
  // also add it to the cart.
  event?.stopPropagation();
  opener = document.activeElement;
  zoomed.value = true;
  document.body.style.overflow = "hidden";
  window.addEventListener("keydown", onKey);
}

function close(event) {
  event?.stopPropagation();
  zoomed.value = false;
  document.body.style.overflow = "";
  window.removeEventListener("keydown", onKey);
  opener?.focus?.();
  opener = null;
}

function onKey(event) {
  if (event.key === "Escape") { event.preventDefault(); close(); return; }
  if (!many.value) return;
  if (event.key === "ArrowRight") { event.preventDefault(); go(1); }
  if (event.key === "ArrowLeft") { event.preventDefault(); go(-1); }
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

// A different product in the same slot starts at its own first image, and never
// leaves the previous product's picture open over it.
watch(() => props.images, () => {
  index.value = 0;
  if (zoomed.value) close();
}, { deep: true });

// A route change unmounts the card mid-view; the page must not be left locked.
onBeforeUnmount(() => {
  if (zoomed.value) close();
});
</script>

<template>
  <div
    v-bind="$attrs"
    class="pic"
    :class="{ 'pic--many': many }"
    @touchstart.passive="onTouchStart"
    @touchend.passive="onTouchEnd"
  >
    <!-- A real button, so the picture is reachable by keyboard and announces what
         it does. `keydown.stop` keeps Enter/Space from also firing the card's own
         add-to-cart handler. -->
    <button
      v-if="zoomable"
      type="button"
      class="pic__zoom"
      :aria-label="`View ${alt} full screen`"
      @click="open"
      @keydown.stop
    >
      <img :src="current" :alt="alt" loading="lazy" class="pic__image" @error="onError" />
    </button>
    <img v-else :src="current" :alt="alt" loading="lazy" class="pic__image" @error="onError" />

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
          @keydown.stop
        />
      </span>
    </template>
  </div>

  <!-- Teleported to the body: the tile clips its own overflow and the card sits
       inside a scrolling grid, so an overlay rendered in place would be cropped
       to a 200px box. -->
  <Teleport to="body">
    <div
      v-if="zoomed"
      class="picbox"
      role="dialog"
      aria-modal="true"
      :aria-label="`${alt} — full screen`"
      @click.self="close"
      @touchstart.passive="onTouchStart"
      @touchend.passive="onTouchEnd"
    >
      <button type="button" class="picbox__close" aria-label="Close full screen" @click="close">&times;</button>

      <button
        v-if="many"
        type="button"
        class="picbox__arrow picbox__arrow--prev"
        :aria-label="`Previous image of ${alt}`"
        @click.stop="go(-1)"
      >&#8249;</button>

      <img :src="current" :alt="alt" class="picbox__image" @error="onError" />

      <button
        v-if="many"
        type="button"
        class="picbox__arrow picbox__arrow--next"
        :aria-label="`Next image of ${alt}`"
        @click.stop="go(1)"
      >&#8250;</button>

      <div class="picbox__bar">
        <strong v-if="alt" class="picbox__title">{{ alt }}</strong>
        <span v-if="many" class="picbox__counter">{{ index + 1 }} / {{ slides.length }}</span>
        <span v-if="many" class="picbox__dots">
          <button
            v-for="(slide, position) in slides"
            :key="slide"
            type="button"
            class="picbox__dot"
            :class="{ 'is-on': position === index }"
            :aria-label="`Show image ${position + 1} of ${slides.length}`"
            :aria-current="position === index"
            @click.stop="select(position)"
          />
        </span>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.pic{position:relative;display:block;width:100%;overflow:hidden;border-radius:.7rem}
/* `contain` rather than `cover`: a product photo that has been cropped to fill a
   tile is a photo of part of the product, which is not what the picker needs. */
.pic__image{display:block;width:100%;height:100%;object-fit:contain}
/* The button is only a hit area -- it must not add a frame or change the layout
   the tile already sets, hence the reset and the inherited size. */
.pic__zoom{display:block;width:100%;height:100%;padding:0;border:0;background:none;cursor:zoom-in}
.pic__zoom:focus-visible{outline:2px solid var(--ref-primary-blue,#2f6bff);outline-offset:-2px;border-radius:.7rem}
.pic__arrow{position:absolute;top:50%;display:flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;transform:translateY(-50%);border:0;border-radius:50%;background:rgba(15,23,42,.55);color:#fff;font-size:22px;line-height:1;cursor:pointer;opacity:0;transition:opacity .15s ease}
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

/* Full-screen viewer ---------------------------------------------------------
   Above the app header (z 1000-ish) and the toast layer, because nothing should
   overlap the thing the user asked to look at. */
.picbox{position:fixed;inset:0;z-index:4000;display:flex;align-items:center;justify-content:center;gap:clamp(.5rem,2vw,1.5rem);padding:clamp(1rem,4vw,3rem);background:rgba(8,12,24,.92);cursor:zoom-out;-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
/* Fills the space rather than sitting at its intrinsic size: a small photo shown
   at 300px in the middle of a black screen reads as broken, and "full screen"
   should mean it. `contain` keeps the aspect ratio, so nothing is ever cropped. */
.picbox__image{flex:1 1 auto;min-width:0;width:100%;height:86vh;max-width:min(1400px,92vw);object-fit:contain;border-radius:.5rem;cursor:default}
.picbox__close{position:absolute;top:clamp(.5rem,2vw,1.25rem);right:clamp(.5rem,2vw,1.25rem);display:flex;align-items:center;justify-content:center;width:44px;height:44px;padding:0;border:0;border-radius:50%;background:rgba(255,255,255,.14);color:#fff;font-size:30px;line-height:1;cursor:pointer}
.picbox__close:hover{background:rgba(255,255,255,.26)}
.picbox__arrow{flex:0 0 auto;display:flex;align-items:center;justify-content:center;width:52px;height:52px;padding:0;border:0;border-radius:50%;background:rgba(255,255,255,.14);color:#fff;font-size:34px;line-height:1;cursor:pointer;transition:background .15s ease}
.picbox__arrow:hover{background:rgba(255,255,255,.28)}
.picbox__bar{position:absolute;right:0;bottom:clamp(.75rem,3vw,1.5rem);left:0;display:flex;flex-direction:column;align-items:center;gap:.45rem;pointer-events:none;color:#fff}
.picbox__title{font-size:14px;font-weight:700;text-shadow:0 1px 4px rgba(0,0,0,.6)}
.picbox__counter{font-size:12px;font-weight:700;opacity:.8;font-variant-numeric:tabular-nums}
.picbox__dots{display:flex;gap:.45rem;pointer-events:auto}
.picbox__dot{width:9px;height:9px;padding:0;border:0;border-radius:50%;background:rgba(255,255,255,.45);cursor:pointer}
.picbox__dot.is-on{background:#fff;transform:scale(1.3)}
/* On a phone the arrows would sit on top of the picture, so the swipe carries the
   sliding and the dots stay as the visible affordance. */
@media (max-width:560px){
  .picbox__arrow{width:40px;height:40px;font-size:26px}
  .picbox__image{max-width:96vw}
}
</style>

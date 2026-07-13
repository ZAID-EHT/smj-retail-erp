<script setup>
defineProps({ node: { type: Object, required: true }, children: { type: Array, default: undefined }, expandedMap: { type: Object, required: true } });
defineEmits(["toggle", "open"]);
</script>
<template>
  <li>
    <div><button class="priority-tree__toggle" type="button" :disabled="!node.expandable" :aria-expanded="node.expandable ? Boolean(children) : undefined" @click="$emit('toggle', node)">{{ node.expandable ? (children ? "−" : "+") : "·" }}</button><button class="priority-tree__label" type="button" @click="$emit('open', node)">{{ node.label }}</button></div>
    <ul v-if="children"><PriorityTreeNode v-for="child in children" :key="child.name" :node="child" :children="expandedMap[child.name]" :expanded-map="expandedMap" @toggle="$emit('toggle', $event)" @open="$emit('open', $event)" /></ul>
  </li>
</template>

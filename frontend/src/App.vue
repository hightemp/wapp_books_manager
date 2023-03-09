<template>
  <div class="main-wrapper">
    <div class="app-mode-panel">
      <router-link to="/" class="btn btn-light"><i class="bi bi-house"></i></router-link>
      <router-link to="/" class="btn btn-light"><i class="bi bi-table"></i></router-link> 
    </div>
    <div class="content-panel">
      <router-view/>
    </div>
  </div>
</template>


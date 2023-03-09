import { createRouter, createWebHistory } from 'vue-router'
import BooksListView from '../views/BooksListView.vue'

const routes = [
  {
    path: '/',
    name: 'books_list',
    component: BooksListView
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router

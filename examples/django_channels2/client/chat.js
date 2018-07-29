import Vue from 'vue'
import apolloProvider from './apollo'
import App from './App.vue'

const app = new Vue({
  provide: apolloProvider.provide(),
  render: h => h(App)
})
app.$mount('#app')

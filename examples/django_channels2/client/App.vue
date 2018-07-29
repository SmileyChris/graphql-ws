<template>
  <div id="app" :class="{disconnected: !connected}">
    <div class="progress" v-if="!connected">
      <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">
        <span>Reconnecting...</span>
      </div>
    </div>
    <ul id="messages" ref="messages">
      <li v-if="loading"><em>loading...</em></li>
      <li v-for="message of messages" :key="`msg-${message.id}`">
        <b v-if="message.name">{{ message.name }}: </b>
        {{ message.message }}
      </li>
    </ul>
    <form @submit.prevent="send">
      <div class="input-group">
        <div class="input-group-prepend">
          <!-- <span class="input-group-text" id="change-name" v-on:click="changeName" title="Change your name">{{ me }}:</span> -->
          <button class="btn" type="button" v-on:click.prevent="changeName" title="Change your name">{{ me }}:</button>
        </div>
        <input class="form-control" ref="message" v-model="message">
        <div class="input-group-append">
          <button class="btn btn-primary" type="submit" :disabled="!connected">Send</button>
        </div>
      </div>
      <i v-if="!connected">reconnecting...</i>
    </form>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import {wsLink} from './apollo'

const MESSAGES_QUERY = gql`query {
  messages {id, name, message}
}`
const MESSAGES_SUB = gql`subscription {
  newMessage {id, name, message}
}`
const SEND_MESSAGE = gql`mutation ($message: String!) {
  sendMessage(message: $message) {id, name, message}
}`
const CHANGE_NAME = gql`mutation ($name: String!) {
  changeName(name: $name) {name}
}`

function addMessage(cachedResult, newMessage) {
  // Bail if the message is already in the cache.
  if (cachedResult.messages.find(m => m.id === newMessage.id)) return
  return Object.assign({}, cachedResult, {messages: [
    ...cachedResult.messages,
    newMessage
  ]})
}

export default {
  apollo: {
    messages: {
      query: MESSAGES_QUERY,
      loadingKey: 'loading',
      subscribeToMore: {
        document: MESSAGES_SUB,
        updateQuery: (previousResult, {subscriptionData: {data: {newMessage}}}) => {
          return addMessage(previousResult, newMessage)
        },
      },
    },
  },
  data: function () {
    return {
      messages: [],
      me: '',
      message: '',
      connected: false,
      loading: false,
    }
  },
  mounted: function () {
    this.$refs.message.focus()
    this.$apollo.query({query: gql`{me}`}).then(({data: {me}}) => this.me=me)
    this.connected = wsLink.subscriptionClient.status === 0
    wsLink.subscriptionClient.on('disconnected', () => {this.connected = false})
    wsLink.subscriptionClient.on('reconnected', () => {this.connected = true})
  },
  methods: {
    changeName(e) {
      const newName = window.prompt('Change your name?', this.me)
      if (newName && this.me !== newName) {
        this.$apollo.mutate({mutation: CHANGE_NAME, variables: {name: newName}}).then(
          ({data: {changeName: {name}}}) => {this.me = name}
        )
      }
      this.$refs.message.focus()
    },
    send(e) {
      const newMessage = this.message
      this.message = ''
      this.$apollo.mutate({
        mutation: SEND_MESSAGE,
        variables: {
          message: newMessage
        },
        update: (store, {data: {sendMessage}}) => {
          const previousData = store.readQuery({query: MESSAGES_QUERY})
          const data = addMessage(previousData, sendMessage)
          if (data) {
            store.writeQuery({query: MESSAGES_QUERY, data})
          }
        },
        optimisticResponse: {
          sendMessage: {
            __typename: 'Message',
            id: new Date(),
            name: this.me,
            message: newMessage,
          },
        },

      }).then((data) => {
        console.debug(data)
      }).catch((error) => {
        console.error(error)
        // restore the message
        if (!this.message) {
          this.message = newMessage
        }
      })
    }
  }
}
</script>

<style>
body {
  margin: 0;
  display: flex;
  height: 100vh;
  flex-direction: column;
}
body > .container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
#app {
  padding: 1em;
  height: 100%;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
#messages li {
  list-style: none;
}
#messages {
  flex-grow: 1;
  border: 1px solid #ccc;
  margin: 0 0 1em;
  padding: .5em;
  overflow: auto;
}
input {
  width: 100%;
  border: 1px solid #555;
}
.disconnected input, .disconnected input:focus {
  border-color: #e55;
}
</style>

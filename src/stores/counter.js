import { defineStore } from "pinia";


export const useCountStore = defineStore("counter", {
  state: () => ({
    isLoading: false,
  }),

  actions: {
    setLoading(value) {
      this.isLoading = value;
    },
  },
});

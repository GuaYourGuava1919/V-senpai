import { defineStore } from "pinia";

export const useCountStore = defineStore("counter", {
  state: () => ({
    isLoading: false,  // ✅ 這裡定義狀態
  }),

  actions: {
    setLoading(value) {
      this.isLoading = value;  // ✅ 正確設定 isLoading
    },
  },
});

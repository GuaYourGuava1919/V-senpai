import { defineStore } from 'pinia'
import { db } from '../config/firebase'
import { doc, getDoc } from 'firebase/firestore'


export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: [],
    }),
    getters: {
        getUser: (state) => state.user

    },
    actions: {
        async fetchUser(uid) {
            try {
                const docRef = doc(db, 'users', uid);
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    this.user = docSnap.data(); // 更新 Pinia 的狀態
                    // console.log(`Document data:`, this.user);
                } else {
                    // console.log('No such document!');
                }
            } catch (error) {
                // console.error('Error fetching document:', error);
            }
        }



    },
    removeItem(itemId) {

    }
})
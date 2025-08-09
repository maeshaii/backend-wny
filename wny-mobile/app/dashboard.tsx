import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert, ActivityIndicator, Modal, TextInput, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { getUserInfo, logoutUser } from '../services/api';

export default function DashboardScreen() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editData, setEditData] = useState({ name: '', course: '', year_graduated: '', profile_pic: '' });
  const router = useRouter();

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      setLoading(true);
      const userInfo = await getUserInfo();
      if (userInfo) {
        setUser(userInfo);
        setEditData({
          name: userInfo.name || '',
          course: userInfo.course || '',
          year_graduated: userInfo.year_graduated ? String(userInfo.year_graduated) : '',
          profile_pic: userInfo.profile_pic || '',
        });
      } else {
        // No user info found, redirect to login
        router.replace('/login');
      }
    } catch (err) {
      setError('Failed to load user information');
      console.error('Error loading user info:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await logoutUser();
              router.replace('/login');
            } catch (err) {
              Alert.alert('Error', 'Failed to logout. Please try again.');
              console.error('Logout error:', err);
            }
          },
        },
      ]
    );
  };

  const handleEditProfile = () => {
    setEditModalVisible(true);
  };

  const handleSaveProfile = () => {
    // Placeholder: just update local state
    setUser({ ...user, ...editData });
    setEditModalVisible(false);
    Alert.alert('Profile updated (not saved to backend)');
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1e3a8a" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadUserInfo}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header with logout button */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard</Text>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Profile Section */}
      {user && (
        <View style={styles.profileCard}>
          <Image
            source={{ uri: user.profile_pic || 'https://randomuser.me/api/portraits/women/44.jpg' }}
            style={styles.profilePic}
          />
          <View style={{ flex: 1 }}>
            <Text style={styles.profileName}>{user.name}</Text>
            <Text style={styles.profileCourse}>{user.course || 'Bachelor of Science in IT'}</Text>
            {user.year_graduated && (
              <Text style={styles.profileBatch}>Batch {user.year_graduated}</Text>
            )}
          </View>
          <TouchableOpacity style={styles.editProfileBtn} onPress={handleEditProfile}>
            <Text style={{ color: '#174f84', fontWeight: 'bold' }}>Edit Profile</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Edit Profile Modal */}
      <Modal
        visible={editModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setEditModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Edit Profile</Text>
            <TextInput
              style={styles.input}
              placeholder="Name"
              value={editData.name}
              onChangeText={(text) => setEditData({ ...editData, name: text })}
            />
            <TextInput
              style={styles.input}
              placeholder="Course"
              value={editData.course}
              onChangeText={(text) => setEditData({ ...editData, course: text })}
            />
            <TextInput
              style={styles.input}
              placeholder="Batch (Year Graduated)"
              value={editData.year_graduated}
              onChangeText={(text) => setEditData({ ...editData, year_graduated: text })}
              keyboardType="numeric"
            />
            <TextInput
              style={styles.input}
              placeholder="Profile Picture URL"
              value={editData.profile_pic}
              onChangeText={(text) => setEditData({ ...editData, profile_pic: text })}
            />
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 20 }}>
              <TouchableOpacity style={styles.saveBtn} onPress={handleSaveProfile}>
                <Text style={{ color: 'white', fontWeight: 'bold' }}>Save</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setEditModalVisible(false)}>
                <Text style={{ color: '#174f84', fontWeight: 'bold' }}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Welcome message */}
      {user && (
        <View style={styles.welcomeContainer}>
          <Text style={styles.welcomeText}>Welcome back, {user.name}!</Text>
        </View>
      )}

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Placeholder for posts */}
        <View style={styles.postCard}>
          <Text style={styles.postAuthor}>Rhodjien Mary P. Caratao</Text>
          <Text style={styles.postContent}>
            Lorem ipsum dolor sit amet. Quo asperiores enim ut veniam repudiandae eum quisquam voluptatem non dolore veritatis eos quia suscipit sed facere alias nam voluptate quia. Ut neque ipsam sed explicabo nemo ut
          </Text>
        </View>
        <View style={styles.postCard}>
          <Text style={styles.postAuthor}>Shaira Mae O. Ma-asin</Text>
          <Text style={styles.postContent}>
            Lorem ipsum dolor sit amet. Quo asperiores enim ut veniam repudiandae eum quisquam voluptatem non dolore veritatis eos quia suscipit sed facere alias nam voluptate quia. Ut neque ipsam sed explicabo nemo ut
          </Text>
        </View>
        <View style={styles.postCard}>
          <Text style={styles.postAuthor}>Alvin D. Paquibot</Text>
          <Text style={styles.postContent}>
            Lorem ipsum dolor sit amet. Quo asperiores enim ut veniam repudiandae eum quisquam voluptatem non dolore veritatis eos quia suscipit sed facere alias nam voluptate quia. Ut neque ipsam sed explicabo nemo ut
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#e74c3c',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#1e3a8a',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1e3a8a',
    paddingHorizontal: 20,
    paddingVertical: 15,
    paddingTop: 50, // Account for status bar
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  logoutButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
  },
  logoutButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    marginHorizontal: 10,
    marginTop: 15,
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  profilePic: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 15,
    backgroundColor: '#e0e7ef',
  },
  profileName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#174f84',
  },
  profileCourse: {
    fontSize: 14,
    color: '#888',
    marginTop: 2,
  },
  profileBatch: {
    fontSize: 13,
    color: '#888',
    marginTop: 2,
  },
  editProfileBtn: {
    backgroundColor: '#e0e7ef',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    marginLeft: 10,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    width: '85%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 4,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#174f84',
    marginBottom: 16,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#eee',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
    fontSize: 15,
    backgroundColor: '#f9f9f9',
  },
  saveBtn: {
    backgroundColor: '#174f84',
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 8,
  },
  cancelBtn: {
    backgroundColor: '#e0e7ef',
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 8,
  },
  welcomeContainer: {
    backgroundColor: 'white',
    padding: 15,
    marginHorizontal: 10,
    marginTop: 10,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  welcomeText: {
    fontSize: 16,
    color: '#174f84',
    fontWeight: 'bold',
  },
  scrollView: {
    marginTop: 10,
    paddingHorizontal: 10,
  },
  postCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
    elevation: 1,
  },
  postAuthor: {
    fontWeight: 'bold',
    color: '#174f84',
    marginBottom: 4,
  },
  postContent: {
    fontSize: 14,
    color: '#333',
  },
}); 
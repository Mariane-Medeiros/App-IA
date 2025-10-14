import React, { useState } from "react";
import { View, Text, Button, Image, StyleSheet, ActivityIndicator } from "react-native";
import * as ImagePicker from "expo-image-picker";
import axios from "axios";

export default function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Abrir câmera ou galeria
  const pickImage = async () => {
    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      setResult(null);
    }
  };

  // Enviar imagem para o servidor
  const sendImage = async () => {
    if (!image) {
      alert("Escolha ou tire uma foto primeiro!");
      return;
    }

    const formData = new FormData();
    formData.append("file", {
      uri: image,
      type: "image/jpeg",
      name: "foto.jpg",
    });

    try {
      setLoading(true);
      const response = await axios.post("https://app-ia-gr9k.onrender.com/predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (error) {
      console.log(error);
      alert("Erro ao enviar imagem");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Classificador de Imagens 🌿</Text>

      <Button title="📷 Tirar Foto" onPress={pickImage} />

      {image && (
        <Image source={{ uri: image }} style={styles.preview} />
      )}

      <Button title="🚀 Enviar para Classificação" onPress={sendImage} disabled={loading} />

      {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}

      {result && (
        <View style={{ marginTop: 20 }}>
          <Text>Classe predita: {result.classe_predita}</Text>
          <Text>Confiança: {(result.confianca * 100).toFixed(2)}%</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#fff" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 20 },
  preview: { width: 250, height: 250, borderRadius: 10, marginVertical: 20 },
});

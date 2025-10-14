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

async function enviarImagem() {
  // Escolher imagem
  let result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: [ImagePicker.MediaType.Images], // atualizado!
    quality: 1,
  });

  if (result.canceled) return;

  // Pega o arquivo
  const file = result.assets[0];
  const formData = new FormData();

  formData.append("file", {
    uri: file.uri,
    name: "imagem.jpg",
    type: "image/jpeg",
  });

  try {
    const response = await fetch("https://meu-backend.onrender.com/predict", {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    const data = await response.json();
    console.log("Resposta do servidor:", data);

  } catch (error) {
    console.error("Erro ao enviar imagem:", error);
  }
}



  return (
    <View style={styles.container}>
      <Text style={styles.title}>Classificador de Imagens 🌿</Text>

      <Button title="📷 Tirar Foto" onPress={pickImage} />

      {image && (
        <Image source={{ uri: image }} style={styles.preview} />
      )}

      <Button title="🚀 Enviar para Classificação" onPress={enviarImagem} disabled={loading} />

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

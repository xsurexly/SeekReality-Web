<template>
  <div class="all">
    <div class="title"></div>
    <div id="map"></div>
  </div>
</template>

<script>
import { onMounted, ref } from "vue"
import * as echarts from "echarts"
import chinaJson from "@/utils/China.json"
import api from "@/api/overviewapi.js"
import { useIdStore } from "@/store/overviewid"
import { ElMessage } from "element-plus"

// 定义地图样式常量
const rangeColor = ['#D7E2FF', '#B5C7FF', '#93ACFF', '#7191FF', '#4F76FF', '#2D5BFF']
const selectedColor = '#FF6B6B'

export default {
  name: 'MapView',
  setup() {
    const idStore = useIdStore()
    const newData = ref(null)
    let chinaMap = null
    const location = "中国"

    function getIdArrayByLocation(location) {
      if (!newData.value) {
        console.error('No data available');
        return;
      }

      let newArr = [];
      try {
        if (location === "中国") {
          // 获取所有省份的数据
          for (const prop in newData.value) {
            if (newData.value[prop]) {
              newArr = newArr.concat(
                newData.value[prop].map(item => item[1])
              );
            }
          }
        } else if (location === "南海诸岛") {
          newArr = [];
        } else if (location !== "nan" && newData.value[location]) {
          // 获取特定省份的数据
          newArr = newData.value[location].map(item => item[1]);
        }
        idStore.setIdArrMap(newArr);
      } catch (error) {
        console.error('Error in getIdArrayByLocation:', error);
      }
    }

    async function updateMapData() {
      try {
        console.log('Fetching map data...');
        const newRawData = await api.getMapData();
        console.log('Received map data:', newRawData);

        if (!newRawData) {
          console.error('No data received from API');
          ElMessage.error('Failed to load map data');
          return;
        }

        // 检查是否有错误信息
        if (newRawData.error) {
          console.error('API returned error:', newRawData.error);
          ElMessage.error(newRawData.error);
          return;
        }

        // 确保数据格式正确
        if (typeof newRawData !== 'object') {
          console.error('Invalid data format received:', typeof newRawData);
          ElMessage.error('Invalid data format received from server');
          return;
        }

        // 验证数据结构
        const hasValidData = Object.keys(newRawData).some(key =>
          Array.isArray(newRawData[key]) && newRawData[key].length > 0
        );

        if (!hasValidData) {
          console.error('No valid location data found in response');
          ElMessage.error('No valid location data available');
          return;
        }

        newData.value = newRawData;
        console.log('Updated newData:', newData.value);

        if (!chinaJson || !chinaJson.features) {
          console.error('Invalid China JSON data');
          ElMessage.error('Map configuration error');
          return;
        }

        // 更新地图数据
        for (let i = 0; i < chinaJson.features.length; i++) {
          let location = chinaJson.features[i].properties.name;
          if (newData.value[location] && Array.isArray(newData.value[location])) {
            chinaJson.features[i].properties.value = newData.value[location].length;
          } else {
            chinaJson.features[i].properties.value = 0;
          }
        }

        // 重新初始化地图
        init();
      } catch (error) {
        console.error('Error updating map data:', error);
        ElMessage.error('Failed to update map data');
      }
    }

    function init() {
      try {
        console.log('Initializing map...');
        if (!chinaJson || !chinaJson.features) {
          console.error('China JSON data is invalid:', chinaJson);
          return;
        }

        echarts.registerMap("china", chinaJson);
        const option = {
          visualMap: {
            min: 0,
            max: 200,
            left: "left",
            top: "bottom",
            text: ["Numbers"],
            dimension: "value",
            inRange: {
              color: rangeColor,
            },
            show: true,
            itemWidth: 15,
            showLabel: true,
            pieces: [
              { min: 200 },
              { min: 150, max: 200 },
              { min: 100, max: 150 },
              { min: 50, max: 100 },
              { min: 0, max: 50 },
              { value: 0 },
            ],
          },
          series: [
            {
              type: "map",
              map: "china",
              top: "28%",
              zoom: 1.7,
              select: {
                itemStyle: {
                  areaColor: selectedColor,
                  label: {
                    show: false,
                  },
                },
              },
              emphasis: {
                itemStyle: {
                  areaColor: selectedColor,
                },
              },
              data: chinaJson.features.map(item => ({
                name: item.properties.name,
                value: item.properties.value || 0,
              })),
            },
          ],
        }

        console.log('Setting map options...');
        chinaMap.setOption(option);

        chinaMap.on("click", (param) => {
          getIdArrayByLocation(param.name);
        });

        console.log('Map initialization complete');
      } catch (error) {
        console.error('Error initializing map:', error);
      }
    }

    onMounted(async () => {
      try {
        console.log('Component mounted');
        const mapElement = document.getElementById("map");
        if (!mapElement) {
          console.error('Map container element not found');
          return;
        }

        chinaMap = echarts.init(mapElement);
        console.log('ECharts instance created');
        getIdArrayByLocation(location[0])
        await updateMapData();
      } catch (error) {
        console.error('Error in onMounted:', error);
      }
    })

    return {
      location
    }
  }
}
</script>

<style scoped>
.all {
  width: 100%;
  height: 100%;
  position: relative;
}

.all > .title {
  font-size: 16px;
  font-weight: bold;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  color: var(--font-color);
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}

#map {
  width: 100%;
  height: 100%;
}

.all:hover {
  transform: translateY(-5px);
}
</style>

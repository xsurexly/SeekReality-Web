<template>
  <div class="overview-container">
    <div class="overview-charts">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <el-icon><Location /></el-icon>
            <span>地理分布视图</span>
          </div>
        </template>
        <div class="chart-content">
          <Map />
        </div>
      </el-card>
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <el-icon><DataLine /></el-icon>
            <span>主题演变视图</span>
          </div>
        </template>
        <div class="chart-content">
          <ThemeRiver />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import Map from "./MapView.vue"
import ThemeRiver from "./ThemeRiver.vue"
import { ref, onMounted } from 'vue';
import { getMapData, getTopicData, getRiverData, getMiddleData, getTreeData } from '@/api/overviewapi';
import { Location, DataLine } from "@element-plus/icons-vue";

export default {
  name: 'OverView',
  components: {
    Location,
    DataLine,
    Map,
    ThemeRiver
  },
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const mapData = ref(null);
    const topicData = ref(null);
    const riverData = ref(null);
    const middleData = ref(null);
    const treeData = ref(null);

    const updateMapChart = async () => {
      try {
        loading.value = true;
        const data = await getMapData();
        mapData.value = data;
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    const updateTopicChart = async () => {
      try {
        loading.value = true;
        const data = await getTopicData();
        topicData.value = data;
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    const updateRiverChart = async () => {
      try {
        loading.value = true;
        const data = await getRiverData();
        riverData.value = data;
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    const updateMiddleChart = async () => {
      try {
        loading.value = true;
        const data = await getMiddleData();
        middleData.value = data;
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    const updateTreeChart = async () => {
      try {
        loading.value = true;
        const data = await getTreeData();
        treeData.value = data;
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      updateMapChart();
      updateTopicChart();
      updateRiverChart();
      updateMiddleChart();
      updateTreeChart();
    });

    return {
      loading,
      error,
      mapData,
      topicData,
      riverData,
      middleData,
      treeData,
      updateMapChart,
      updateTopicChart,
      updateRiverChart,
      updateMiddleChart,
      updateTreeChart
    };
  }
}
</script>

<style scoped>
.overview-container {
  width: 100%;
  box-sizing: border-box;
  padding: 20px 0;
}

.overview-charts {
  display: flex;
  gap: 20px;
  width: 100%;
}

.chart-card {
  flex: 1;
  height: 400px;
  transition: transform 0.3s;
  background: var(--navbar-bg);
  color: var(--font-color);
  border: 0px solid #b5b5b5;
}

.chart-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 16px;
  gap: 8px;
}

.chart-content {
  height: calc(100% - 40px);
  width: 100%;
}

:deep(.el-card__body) {
  height: calc(100% - 55px);
  padding: 0;
}
</style>

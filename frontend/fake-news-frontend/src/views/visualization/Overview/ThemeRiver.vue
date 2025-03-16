<template>
  <div class="all">
    <div id="river"></div>
  </div>
</template>

<script>
import * as d3 from "d3"
import { onMounted, ref, watch } from "vue"
import api from "@/api/overviewapi.js"
import { storeToRefs } from "pinia"
import { useIdStore } from "@/store/overviewid.js"
import { topicColour, topics } from "@/utils/overviewtopic.js"
import { Legend } from "@/utils/River/legendStyle.js"
import { TimeLine } from "@/utils/River/timeLineStyle.js"
import { River } from "@/utils/River/riverStyle.js"
import { ElMessage } from "element-plus"

export default {
  name: 'ThemeRiver',
  setup() {
    const idStore = useIdStore()
    const { idArrMap } = storeToRefs(idStore)
    const mapData = ref([])
    const popTextTopic = ref("")
    const popTextPos = ref([])
    const dataSortByTopic = ref([])
    const dataSortByTopicTotal = ref([])
    const mapDataTotal = ref([])
    const xDomain = ref([])
    const xDomainTotal = ref([])
    let keywordsId = ref([])
    let svg = ref(null)
    let x = ref(null)
    let y = ref(null)

    const translate = new Map([
      ["社会时事", "Current Events"],
      ["国际", "World News"],
      ["娱乐", "Entertainment"],
      ["军事", "Military"],
      ["科技", "Technology"],
      ["历史文化", "Culture"],
      ["常识", "Common Sense"],
      ["母婴育儿", "Baby Care"],
      ["教育", "Education"],
      ["情感", "Affection"],
    ])

    async function updateTopicData() {
      try {
        console.log('Fetching topic data...');
        const newData = await api.getTopicData();
        console.log('Received topic data:', newData);

        if (!newData) {
          console.error('No data received from API');
          ElMessage.error('Failed to load topic data');
          return;
        }

        // 检查是否有错误信息
        if (newData.error) {
          console.error('API returned error:', newData.error);
          ElMessage.error(newData.error);
          return;
        }

        console.log('Sorting data...');
        const sortedData = sortData(newData);
        console.log('Sorted data:', sortedData);

        if (!sortedData || !sortedData.length) {
          console.error('No sorted data available');
          ElMessage.error('No valid topic data available');
          return;
        }

        console.log('Getting final data...');
        mapData.value = getFinalData(sortedData);
        console.log('Final data:', mapData.value);

        if (!mapData.value || !mapData.value.length) {
          console.error('No final data available');
          ElMessage.error('Failed to process topic data');
          return;
        }

        mapDataTotal.value = JSON.parse(JSON.stringify(mapData.value));
        console.log('Starting TopicData...');
        TopicData();
      } catch (error) {
        console.error('Error updating topic data:', error);
        ElMessage.error('Failed to update topic data');
      }
    }

    watch(idArrMap, () => {
      svg.value.selectAll(".keyword").remove()
      mapData.value = JSON.parse(JSON.stringify(mapDataTotal.value))
      for (let index in mapData.value) {
        for (let key in mapData.value[index].ids) {
          mapData.value[index].ids[key] = mapData.value[index].ids[key].filter(
            (id) => idArrMap.value?.includes(id)
          )
          mapData.value[index][key] = mapData.value[index].ids[key].length
        }
      }
      TopicData()
      dataSortByTime()
      drawMain()
    })

    function sortData(newData) {
      try {
        console.log('Starting sortData with:', newData);
        if (!newData || typeof newData !== 'object') {
          console.error('Invalid newData:', newData);
          return [];
        }

        let sortedData = [];
      for (let key in newData) {
        let newKeys = {
          "Current Events": 0,
          "World News": 0,
          Entertainment: 0,
          Military: 0,
          Technology: 0,
          Culture: 0,
          "Common Sense": 0,
          "Baby Care": 0,
          Education: 0,
          Affection: 0,
          date: "",
          ids: {},
          };

          // 确保数据格式正确
          if (!newData[key] || !newData[key].date || !Array.isArray(newData[key].topic)) {
            console.error(`Invalid data structure for key ${key}:`, newData[key]);
            continue;
          }

          newKeys.date = newData[key].date;

          // 处理主题数据
          newData[key].topic.forEach((item) => {
            if (!item || !item.name || typeof item.num !== 'number') {
              console.error('Invalid topic item:', item);
              return;
            }

            let keyName = translate.get(item.name);
            if (!keyName) {
              console.error(`No translation found for topic: ${item.name}`);
              return;
            }

            if (keyName === "date") return;

            // 设置主题数量
            newKeys[keyName] = item.num;

            // 设置主题对应的 ID 列表
            if (item.id && Array.isArray(item.id)) {
              newKeys.ids[keyName] = item.id;
            } else {
              newKeys.ids[keyName] = [];
              console.warn(`No valid IDs for topic ${item.name}`);
            }
          });

          sortedData.push(newKeys);
        }

        if (sortedData.length === 0) {
          console.error('No valid data processed');
          return [];
        }

        // 按日期排序
        sortedData.sort((a, b) => (a.date > b.date ? 1 : -1));
        console.log('Sorted data result:', sortedData);
        return sortedData;
      } catch (error) {
        console.error('Error in sortData:', error);
        return [];
      }
    }

    function groupDataByWeek(data) {
      const format = d3.timeFormat("%Y-%b-%U")
      let groupedData = {}
      data.forEach((item) => {
        let week = format(new Date(item.date))
        if (!groupedData[week]) {
          groupedData[week] = [item]
        } else {
          groupedData[week].push(item)
        }
      })
      return groupedData
    }

    function calculateTopicKeys(data) {
      let resKeys = {
        "Current Events": 0,
        "World News": 0,
        Entertainment: 0,
        Military: 0,
        Technology: 0,
        Culture: 0,
        "Common Sense": 0,
        "Baby Care": 0,
        Education: 0,
        Affection: 0,
      }
      data.forEach((item) => {
        for (let key in item) {
          if (key !== "date" && key !== "ids") {
            resKeys[key] += item[key]
          }
        }
      })
      return resKeys
    }

    function getIds(data) {
      const ids = {}
      data.forEach((item) => {
        for (let key in item.ids) {
          if (!ids[key]) {
            ids[key] = item.ids[key]
          } else {
            ids[key] = ids[key].concat(item.ids[key])
          }
        }
      })
      return ids
    }

    function getFinalData(data) {
      const groupedData = groupDataByWeek(data)
      const res = Object.entries(groupedData).map(([date, item]) => {
        let resKeys = calculateTopicKeys(item)
        let ids = getIds(item)
        return {
          date: date,
          ...resKeys,
          ids: ids,
        }
      })
      return res
    }

    function popText(topic) {
      popTextPos.value = []
      const datetoweek = d3.timeParse("%Y-%b-%U")
      const target = dataSortByTopic.value.find(
        (item) => item.key === topic
      )
      if (!target) return

      for (let mon = 1; mon <= 12; mon++) {
        let day = mon === 8 ? 3 : mon === 10 ? 7 : 1
        let formatTime = d3.timeFormat("%Y-%b-%U")(new Date(`2020-${mon}-${day}`))
        let pos = { x: 0, y: 0 }
        pos.x = x.value(datetoweek(formatTime))
        let foundItem = target.values.find(
          (item) => item.date === formatTime
        )
        if (!foundItem) continue
        pos.y = y.value(foundItem.number)
        popTextPos.value[mon] = pos
      }
    }

    function setLegend() {
      // 创建背景矩形，使图例更加明显
      svg.value
        .append("rect")
        .attr("x", Legend.xOffsets - 10)
        .attr("y", Legend.yOffsets - 25)
        .attr("width", 180) // 增加宽度以适应更大的字体
        .attr("height", (topicColour.length + 1) * Legend.verticalSpacing + 20)
        .attr("rx", 8)
        .attr("ry", 8)
        .attr("fill", "white")
        .attr("stroke", "#eee")
        .attr("stroke-width", 1)
        .attr("opacity", 0.95);

      // 添加图例标题
      svg.value
        .append("text")
        .attr("x", Legend.xOffsets + 90) // 调整标题位置
        .attr("y", Legend.yOffsets - 5)
        .style("text-anchor", "middle")
        .style("font-size", "18px") // 增大标题字体
        .style("font-weight", "bold")
        .text("Topics");

      // 单列垂直排列所有主题
      const legend = svg.value
        .selectAll(".legend")
        .data(topicColour)
        .enter()
        .append("g")
        .attr("class", "legend")
        .attr("transform", (d, i) =>
          `translate(${Legend.xOffsets},${i * Legend.verticalSpacing + Legend.yOffsets})`
        );

      legend
        .append("rect")
        .attr("x", Legend.rectXOffsets)
        .attr("y", Legend.rectYOffsets)
        .attr("rx", Legend.rectR)
        .attr("ry", Legend.rectR)
        .attr("width", Legend.rectLength)
        .attr("height", Legend.rectLength)
        .style("fill", (d) => d.colour);

      legend
        .append("text")
        .attr("x", Legend.textXOffsets)
        .attr("y", Legend.textYOffsets)
        .style("text-anchor", "start")
        .style("font-size", "16px") // 确保文字大小一致
        .text((d) => d.topic);

      // 为所有图例添加点击事件
      svg.value.selectAll(".legend").on("click", (d) => {
        popTextTopic.value = d.target.__data__.topic;
        setRiverKeywords(popTextTopic.value);
        popText(popTextTopic.value);
      });
    }

    async function setRiverKeywords(topic) {
      keywordsId.value = []
      const target = dataSortByTopicTotal.value.find(
        (item) => item.key === topic
      )
      if (!target) return

      target.values.forEach((item) => {
        if (item.ids !== undefined) {
          item.ids.forEach((id) => {
            keywordsId.value.push(id)
          })
        }
      })

      const rawKeyword = await api.sendRiverKeywords(keywordsId.value)
      let keyword = []
      for (let [key, value] of Object.entries(rawKeyword)) {
        const topic = Object.keys(value)[0]
        let month = Number(key)
        if (topic) {
          keyword.push({
            month: month,
            word: value[topic][0],
          })
        }
      }
      addKeyword(keyword)
    }

    function addKeyword(keyword) {
      svg.value.selectAll(".keyword").remove()
      let kwSiftedByTime = keyword.filter((item) =>
        popTextPos.value[item.month] !== undefined
      )

      const kw = svg.value
        .selectAll(".keyword")
        .data(kwSiftedByTime)
        .enter()
        .append("g")
        .attr("class", "keyword")

      let text = kw
        .append("text")
        .attr("x", (d) => popTextPos.value[d.month].x + River.xOffSet)
        .attr("y", (d) => popTextPos.value[d.month].y + River.yOffSet)
        .text((d) => d.word)
        .style("fill", "white")
        .style("text-anchor", "middle")

      svg.value
        .selectAll(".keyword")
        .selectAll("text")
        .each(function(d) {
          d.bbox = this.getBBox()
        })

      kw.append("rect")
        .attr("x", (d) => d.bbox ? d.bbox.x - 3 : 0)
        .attr("y", (d) => d.bbox ? d.bbox.y - 1 : 0)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", (d) => d.bbox ? d.bbox.width + 5 : 0)
        .attr("height", (d) => d.bbox ? d.bbox.height + 1 : 0)
        .style("fill", "#717d8e")
        .style("opacity", 1)

      text.raise()
    }

    function getXDomain() {
      try {
        if (!mapData.value || !mapData.value.length) {
          console.error('No data for xDomain calculation');
          return [null, null];
        }
        const datetoweek = d3.timeParse("%Y-%b-%U");
        return [
          datetoweek(mapData.value[0].date),
          datetoweek(mapData.value[mapData.value.length - 1].date),
        ];
      } catch (error) {
        console.error('Error in getXDomain:', error);
        return [null, null];
      }
    }

    function getYDomain() {
      if (!mapData.value || !mapData.value.length) {
        return [0, 0]
      }
      const yRawDomain = []
      mapData.value.forEach((item) => {
        for (let key in item) {
          if (key !== "date" && key !== "ids") {
            yRawDomain.push(item[key])
          }
        }
      })
      return [d3.max(yRawDomain) || 0, d3.min(yRawDomain) || 0]
    }

    function TopicData() {
      try {
        console.log('Starting TopicData function');
        console.log('Current mapData:', mapData.value);

        // 验证地图数据
        if (!mapData.value || !Array.isArray(mapData.value) || mapData.value.length === 0) {
          console.error('Invalid or empty mapData:', mapData.value);
          ElMessage.error('No valid data available');
          return;
        }

        // 获取并验证时间域
        const newXDomain = getXDomain();
        if (!newXDomain || !newXDomain[0] || !newXDomain[1]) {
          console.error('Invalid xDomain from getXDomain:', newXDomain);
          ElMessage.error('Failed to calculate time range');
          return;
        }
        xDomain.value = newXDomain;
        console.log('Set xDomain:', xDomain.value);

        // 处理主题数据
        console.log('Processing topic data...');
        const processedData = dataSortByTime();
        console.log('Processed data:', processedData);

        if (!processedData || !Array.isArray(processedData) || processedData.length === 0) {
          console.error('Failed to process topic data');
          ElMessage.error('Failed to process topic data');
          return;
        }

        // 更新数据
        dataSortByTopic.value = processedData;
        dataSortByTopicTotal.value = JSON.parse(JSON.stringify(processedData));
        console.log('Updated dataSortByTopic:', dataSortByTopic.value);

        // 绘制主视图
        console.log('Drawing main view...');
        drawMain();
        console.log('TopicData function completed');
      } catch (error) {
        console.error('Error in TopicData:', error);
        ElMessage.error('Failed to process topic data');
      }
    }

    function dataSortByTime() {
      try {
        console.log('Starting dataSortByTime');
        console.log('Current xDomain:', xDomain.value);
        console.log('Current mapData:', mapData.value);

        if (!xDomain.value || !xDomain.value[0] || !xDomain.value[1]) {
          console.error('Invalid xDomain:', xDomain.value);
          return [];
        }

        const timeParse = d3.timeParse("%Y-%b-%U");

        // 确保 mapData.value 是有效的数组
        if (!mapData.value || !Array.isArray(mapData.value) || mapData.value.length === 0) {
          console.error('Invalid or empty mapData:', mapData.value);
          return [];
        }

        // 创建主题数据结构
        const topicData = {};
        topics.forEach(topic => {
          topicData[topic] = {
            key: topic,
            values: []
          };
        });

        // 处理每个时间点的数据
        mapData.value.forEach(item => {
          if (!item || !item.date) {
            console.warn('Invalid item in mapData:', item);
            return;
          }

          const date = timeParse(item.date);
          if (!date) {
            console.warn('Failed to parse date:', item.date);
            return;
          }

          // 检查日期是否在范围内
          if (date < xDomain.value[0] || date > xDomain.value[1]) {
            return;
          }

          // 处理每个主题的数据
          topics.forEach(topic => {
            if (typeof item[topic] === 'number' && item[topic] > 0) {
              topicData[topic].values.push({
                date: item.date,
                number: item[topic],
                ids: Array.isArray(item.ids?.[topic]) ? item.ids[topic] : []
              });
            }
          });
        });

        // 转换数据结构为数组并过滤掉空值
        const result = Object.values(topicData)
          .filter(item => item.values.length > 0)
          .map(item => ({
            ...item,
            values: item.values.sort((a, b) => {
              const dateA = timeParse(a.date);
              const dateB = timeParse(b.date);
              return dateA - dateB;
            })
          }));

        console.log('Processed topic data:', result);

        if (result.length === 0) {
          console.error('No valid topic data processed');
          return [];
        }

        // 收集所有 ID
        const idArr = [];
        result.forEach(item => {
          item.values.forEach(value => {
            if (Array.isArray(value.ids)) {
              idArr.push(...value.ids);
            }
          });
        });

        // 更新 store
        if (idArr.length > 0) {
          idStore.setIdArrRiver(idArr);
        } else {
          console.warn('No IDs collected from data');
        }

        return result;
      } catch (error) {
        console.error('Error in dataSortByTime:', error);
        return [];
      }
    }

    function findTime(date, index) {
      const dataParse = d3.timeParse("%Y-%b-%U")
      let finded
      dataSortByTopicTotal.value.find((item) => {
        let data = index === 1 ? item.values : [...item.values].reverse()
        data.find((value) => {
          let valueDate = dataParse(value.date)
          if (!valueDate) return false
          if (index === 1) {
            if (valueDate >= date) {
              finded = valueDate
              return true
            }
            return false
          } else {
            if (valueDate <= date) {
              finded = valueDate
              return true
            }
            return false
          }
        })
      })
      return finded
    }

    function setTimeLine() {
      xDomain.value = getXDomain()
      xDomainTotal.value = getXDomain()
      if (!xDomain.value[0] || !xDomain.value[1]) return
      xDomain.value = [new Date(xDomain.value[0]), new Date(xDomain.value[1])]

      const year = xDomain.value[1]?.getFullYear().toString()
      const formatTime = d3.timeFormat("%b-%U")
      const formatTick = (domainValue) => formatTime(domainValue)
      let selectedNum = 0
      let selectedDate = []

      // 为图例留出更多空间
      const chartWidth = River.width - River.margin.left - River.margin.right - 200; // 增加右侧边距

      let timelineX = d3.scaleTime()
        .domain(xDomain.value)
        .range([0, chartWidth])

      // 添加时间轴标题
      svg.value
        .append("text")
        .attr("x", (chartWidth / 2) + River.margin.left)
        .attr("y", TimeLine.textYOffSet - 15)
        .style("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .text("Time (Click to filter by time range)")

      svg.value
        .append("g")
        .attr(
          "transform",
          `translate(${River.margin.left},${TimeLine.timeYOffSet})`
        )
        .attr("class", "pointer")
        .style("font", TimeLine.timeFont)
        .call(
          d3.axisBottom(timelineX)
            .ticks(d3.timeMonth)
            .tickFormat(formatTick)
            .tickSize(0)
        )
        .call((g) => g.select(".domain").remove())
        .on("click", (param) => {
          svg.value.select(".keyword").remove()
          if (selectedNum >= 2) {
            svg.value.selectAll("text[fill='#17a2b88f']").attr("fill", "black")
            selectedNum = 0
            selectedDate = []
            xDomain.value = xDomainTotal.value
          }
          d3.select(param.target).attr("fill", "#17a2b88f")
          selectedNum++
          if (selectedNum === 1) {
            let time = findTime(param.target.__data__, 1)
            time && selectedDate.push(time)
            xDomain.value = [selectedDate[0], xDomain.value[1]]
          }
          if (selectedNum === 2) {
            let time = findTime(param.target.__data__, 2)
            time && selectedDate.push(time)
            if (selectedDate[0] > selectedDate[1]) {
              selectedDate.reverse()
            }
            xDomain.value = selectedDate
          }
          dataSortByTime()
          drawMain()
        })

      svg.value
        .append("line")
        .attr("x1", River.margin.left)
        .attr("y1", TimeLine.timeYOffSet)
        .attr("x2", River.margin.left + chartWidth)
        .attr("y2", TimeLine.timeYOffSet)
        .attr("stroke", TimeLine.lineColor)
        .attr("opacity", TimeLine.lineOpacity)
        .attr("stroke-width", TimeLine.timeStrokeWidth)

      svg.value
        .append("text")
        .attr("x", River.margin.left)
        .attr("y", TimeLine.textYOffSet - 30)
        .style("text-anchor", "start")
        .attr("font-size", TimeLine.textFont)
        .attr("font-weight", TimeLine.textWeight)
        .text(year)
    }

    let xAxis, yAxis, river
    function drawMain() {
      try {
        console.log('Starting drawMain with data:', dataSortByTopic.value);

        if (!svg.value) {
          console.error('SVG element not initialized');
          return;
        }

        if (!xDomain.value || !xDomain.value[0] || !xDomain.value[1]) {
          console.error('Invalid xDomain:', xDomain.value);
          return;
        }

        // 移除现有的元素
        xAxis && xAxis.remove();
        yAxis && yAxis.remove();
        river && river.remove();

        // 验证数据
        if (!dataSortByTopic.value || !Array.isArray(dataSortByTopic.value)) {
          console.error('Invalid dataSortByTopic:', dataSortByTopic.value);
          return;
        }

        // 计算所有主题数据的最大值，用于 y 轴比例尺
        let allValues = [];
        dataSortByTopic.value.forEach(topic => {
          if (topic && topic.values && Array.isArray(topic.values)) {
            topic.values.forEach(v => {
              if (v && typeof v.number === 'number' && v.number >= 0) {
                allValues.push(v.number);
              }
            });
          }
        });

        const maxY = Math.max(d3.max(allValues) || 0, 10);
        console.log('Max Y value:', maxY);

        const formatTime = d3.timeFormat("%b-%U");
        const formatTick = (domainValue) => formatTime(domainValue);

        // 调整图表尺寸和边距
        const chartWidth = River.width - River.margin.left - River.margin.right;
        const chartHeight = River.height - River.margin.top - River.margin.bottom;

        // 设置 x 轴比例尺
        x.value = d3.scaleTime()
          .domain(xDomain.value)
          .range([0, chartWidth]);

        // 绘制 x 轴
        xAxis = svg.value
          .append("g")
          .attr(
            "transform",
            `translate(${River.margin.left},${chartHeight + River.margin.top})`
          )
          .call(
            d3.axisBottom(x.value)
              .ticks(d3.timeMonth)
              .tickFormat(formatTick)
              .tickSize(0)
          );

        // 调整 x 轴标签
        xAxis.selectAll("text")
          .style("text-anchor", "end")
          .attr("dx", "-.8em")
          .attr("dy", ".15em")
          .attr("transform", "rotate(-45)")
          .style("font-size", "16px")
          .style("font-weight", "500");

        // 设置 y 轴比例尺
        y.value = d3.scaleLinear()
          .domain([0, maxY * 1.2])
          .range([chartHeight, 0])
          .nice();

        // 绘制 y 轴
        yAxis = svg.value
          .append("g")
          .attr("transform", `translate(${River.margin.left},${River.margin.top})`)
          .call(d3.axisLeft(y.value)
            .tickSize(-chartWidth)
            .ticks(10))
          .call((g) => g.select(".domain").remove());

        // 添加 y 轴标题
        svg.value
          .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", River.margin.left / 3)
          .attr("x", -(River.height / 2))
          .attr("dy", "1em")
          .style("text-anchor", "middle")
          .style("font-size", "16px")
          .style("font-weight", "bold")
          .text("Number of Rumors");

        // 添加网格线
        svg.value.selectAll(".tick line")
          .attr("opacity", 0.15)
          .attr("stroke-dasharray", "2,2");

        // 绘制河流图
        river = svg.value
          .append("g")
          .attr("transform", `translate(${River.margin.left},${River.margin.top})`);

        // 解析时间
        const parse = d3.timeParse("%Y-%b-%U");

        // 绘制河流图
        river.selectAll(".line")
          .data(dataSortByTopic.value.filter(d => d && d.values && Array.isArray(d.values)))
        .enter()
        .append("path")
          .attr("class", "topic-line")
        .attr("stroke", (d) => {
            if (!d || !d.key) return "black";
            let topic = topicColour.find((item) => item.topic === d.key);
            return topic ? topic.colour : "black";
        })
        .attr("stroke-width", River.lineStrokeWidth)
        .attr("fill", "none")
        .attr("opacity", 0.85)
        .attr("d", (d) => {
            if (!d || !d.values || !Array.isArray(d.values)) return "";

            // 过滤有效值并确保数据点按日期排序
            const validValues = d.values
              .filter(v => {
                // 确保值有效
                if (!v || !v.date || typeof v.number !== 'number' || v.number < 0) return false;

                // 确保日期在x轴范围内
                const parsedDate = parse(v.date);
                return parsedDate && parsedDate >= xDomain.value[0] && parsedDate <= xDomain.value[1];
              })
              .sort((a, b) => {
                const dateA = parse(a.date);
                const dateB = parse(b.date);
                return dateA - dateB;
              });

            if (validValues.length === 0) return "";

            // 确保每个主题至少有两个点，以便绘制线条
            if (validValues.length === 1) {
              // 如果只有一个点，复制它并稍微偏移，以便能绘制线条
              const point = validValues[0];
              const date = parse(point.date);
              if (date) {
                // 创建一个偏移一天的新点
                const newDate = new Date(date);
                newDate.setDate(newDate.getDate() + 1);
                // 确保新日期仍在x轴范围内
                if (newDate <= xDomain.value[1]) {
                  const newDateStr = d3.timeFormat("%Y-%b-%U")(newDate);
                  validValues.push({
                    date: newDateStr,
                    number: point.number,
                    ids: [...(point.ids || [])]
                  });
                }
              }
            }

            // 使用 d3.line 绘制线条，使用 curveCardinal 曲线使线条更平滑
            // 添加clipPath以确保线条不超出x轴范围
            return d3
              .line()
                .curve(d3.curveCardinal.tension(0.4))
                .defined(v => {
                  const parsedDate = parse(v.date);
                  // 确保点在x轴范围内
                  return parsedDate !== null &&
                         !isNaN(v.number) &&
                         parsedDate >= xDomain.value[0] &&
                         parsedDate <= xDomain.value[1];
                })
                .x((v) => {
                  const parsedDate = parse(v.date);
                  // 确保x坐标不小于0
                  const xCoord = parsedDate ? x.value(parsedDate) : 0;
                  return Math.max(0, xCoord);
                })
                .y((v) => y.value(v.number))(validValues);
          });

        // 添加剪切路径，确保线条不超出绘图区域
        svg.value
          .append("defs")
          .append("clipPath")
          .attr("id", "chart-area")
          .append("rect")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", chartWidth)
          .attr("height", chartHeight);

        // 应用剪切路径
        river.attr("clip-path", "url(#chart-area)");

        console.log('drawMain completed successfully');
      } catch (error) {
        console.error('Error in drawMain:', error);
      }
    }

    function drawThemeRiver() {
      try {
        console.log('Starting drawThemeRiver');
        if (!mapData.value || !mapData.value.length) {
          console.error('No data available for drawing');
          return;
        }

        // 清除现有的图形
        svg.value.selectAll("*").remove();

        // 设置时间轴
        setTimeLine();

        // 设置图例
        setLegend();

        // 绘制主视图
        drawMain();

        console.log('Theme river drawing completed');
      } catch (error) {
        console.error('Error in drawThemeRiver:', error);
        ElMessage.error('Failed to draw theme river');
      }
    }

    onMounted(async () => {
      try {
        console.log('Component mounted');
        const riverElement = document.getElementById("river");
        if (!riverElement) {
          console.error('River container element not found');
          return;
        }

        console.log('Creating SVG...');
        svg.value = d3.select("#river")
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
          .attr("viewBox", `0 0 ${River.width} ${River.height}`)
          .attr("preserveAspectRatio", "xMidYMid meet")
          .style("max-width", "100%")
          .style("max-height", "100%");

        console.log('Fetching initial data...');
        await updateTopicData();

        // 确保数据加载完成后调用 drawThemeRiver
        if (mapData.value && mapData.value.length > 0) {
          console.log('Drawing theme river...');
          drawThemeRiver();
        }
      } catch (error) {
        console.error('Error in onMounted:', error);
        ElMessage.error('Failed to initialize theme river view');
      }
    })

    return {
      getYDomain,
      mapData,
      popTextTopic,
      popTextPos,
      dataSortByTopic,
      svg,
      x,
      y
    }
  }
}
</script>

<style>
.all {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

#river {
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: visible;
  padding: 20px;
  height: calc(100vh - 200px); /* 设置一个合适的高度 */
}

#river svg {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%) scale(0.95); /* 居中并稍微缩小以确保完全可见 */
}

.legend {
  stroke-width: 1;
  stroke: black;
  stroke-opacity: 0;
  cursor: pointer;
}

.legend:hover {
  stroke-opacity: 0.7;
  stroke-width: 2;
}

.legend text {
  font-size: 16px;
  fill: var(--font-color);
}

.pointer {
  cursor: pointer;
}

.pointer text {
  font-size: 16px;
  font-weight: 500;
  fill: var(--font-color);
}

.pointer text:hover {
  fill: #17a2b8;
  font-weight: bold;
}

.topic-line {
  stroke-linejoin: round;
  stroke-linecap: round;
  transition: stroke-width 0.2s;
  fill: none;
  opacity: 0.85;
}

.topic-line:hover {
  stroke-width: 3;
  opacity: 1;
}

.tick line {
  stroke: #eee;
  stroke-width: 0.7;
}

.tick text {
  font-size: 16px;
  font-weight: 500;
  fill: var(--font-color);
}

/* 添加新的样式以确保时间轴标签可见 */
.x-axis text {
  font-size: 11px;
  fill: var(--font-color);
}
</style>

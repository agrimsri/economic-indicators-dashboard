import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import * as echarts from 'echarts'
import type { SeriesData } from '../../types/dashboard'
import { axisStyle, commonChartTheme } from './chartUtils'

interface GstChartProps {
  series: SeriesData[]
}

export const GstChart: React.FC<GstChartProps> = ({ series }) => {
  const option = useMemo(() => {
    const gstSeries = series.find(
      (s) => s.key === 'gross_gst' || s.label.toLowerCase().includes('gross')
    )
    const yoySeries = series.find(
      (s) => s.key === 'yoy_growth' || s.label.toLowerCase().includes('yoy')
    )

    const categories = (gstSeries?.points || []).map((p) => p.x)
    const barData = (gstSeries?.points || []).map((p) => p.y)
    const lineData = categories.map((cat) => {
      const pt = yoySeries?.points.find((p) => p.x === cat)
      return pt?.y ?? null
    })

    return {
      ...commonChartTheme,
      legend: {
        ...commonChartTheme.legend,
        data: ['Gross GST (₹ lakh cr)', 'YoY Growth (%)'],
      },
      xAxis: {
        type: 'category',
        data: categories,
        ...axisStyle,
      },
      yAxis: [
        {
          type: 'value',
          name: '₹ Lakh Cr',
          nameTextStyle: { color: '#94a3b8', fontSize: 11 },
          ...axisStyle,
          axisLabel: {
            ...axisStyle.axisLabel,
            formatter: '₹{value}',
          },
        },
        {
          type: 'value',
          name: 'YoY %',
          nameTextStyle: { color: '#94a3b8', fontSize: 11 },
          ...axisStyle,
          splitLine: { show: false }, // Avoid duplicate gridlines
          axisLabel: {
            ...axisStyle.axisLabel,
            formatter: '{value}%',
          },
        },
      ],
      series: [
        {
          name: 'Gross GST (₹ lakh cr)',
          type: 'bar',
          yAxisIndex: 0,
          data: barData,
          barMaxWidth: 24,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#0fb8e6' },
              { offset: 1, color: '#042a4d' },
            ]),
          },
        },
        {
          name: 'YoY Growth (%)',
          type: 'line',
          yAxisIndex: 1,
          data: lineData,
          showSymbol: true,
          symbolSize: 8,
          itemStyle: {
            color: '#f4e15c',
          },
          lineStyle: {
            width: 2.5,
            color: '#f4e15c',
          },
        },
      ],
    }
  }, [series])

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '290px' }}>
      <ReactECharts
        option={option}
        style={{ width: '100%', height: '100%', minHeight: '290px' }}
        opts={{ renderer: 'canvas' }}
        notMerge={true}
      />
    </div>
  )
}

module.exports = {
  root: true,
  env: {
    node: true,
    'vue/setup-compiler-macros': true
  },
  'extends': [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  parserOptions: {
    parser: '@babel/eslint-parser',
    ecmaVersion: 2020
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    "vue/multi-word-component-names":"off",
    "no-self-assign": "off"
  },
  "globals":{
    "error":true
  },
  overrides: [
        //这里是添加的代码
        {
          files: ['src/views/index.vue','src/views/**/index.vue'],   // 匹配views和二级目录中的index.vue
          rules: {
          'vue/multi-word-component-names':"off",
          } //给上面匹配的文件指定规则
        },
    {
      files: [
        '**/__tests__/*.{j,t}s?(x)',
        '**/tests/unit/**/*.spec.{j,t}s?(x)'
      ],
      env: {
        jest: true
      }
    }
  ]
}

